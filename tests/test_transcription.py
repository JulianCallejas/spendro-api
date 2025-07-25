import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import tempfile
import os
from io import BytesIO

def test_transcribe_audio_success(client, test_user, auth_headers):
    """Test successful audio transcription."""
    # Create a mock audio file
    audio_content = b"fake_audio_content"
    
    with patch('app.services.transcription_service.transcription_service') as mock_service:
        # Mock the service methods
        mock_service.is_available.return_value = True
        mock_service.transcribe_audio.return_value = {
            "text": "Hola, esto es una prueba de transcripción",
            "language": "es",
            "duration": 5.2,
            "confidence": 0.95
        }
        
        response = client.post(
            "/api/v1/transcription/transcribe",
            headers=auth_headers,
            files={"audio_file": ("test.wav", BytesIO(audio_content), "audio/wav")}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["text"] == "Hola, esto es una prueba de transcripción"
        assert data["language"] == "es"
        assert data["duration"] == 5.2
        assert data["confidence"] == 0.95

def test_transcribe_audio_service_unavailable(client, test_user, auth_headers):
    """Test transcription when service is unavailable."""
    audio_content = b"fake_audio_content"
    
    with patch('app.services.transcription_service.transcription_service') as mock_service:
        mock_service.is_available.return_value = False
        
        response = client.post(
            "/api/v1/transcription/transcribe",
            headers=auth_headers,
            files={"audio_file": ("test.wav", BytesIO(audio_content), "audio/wav")}
        )
        
        assert response.status_code == 503
        assert "not available" in response.json()["detail"]

def test_transcribe_audio_unsupported_format(client, test_user, auth_headers):
    """Test transcription with unsupported audio format."""
    audio_content = b"fake_audio_content"
    
    response = client.post(
        "/api/v1/transcription/transcribe",
        headers=auth_headers,
        files={"audio_file": ("test.txt", BytesIO(audio_content), "text/plain")}
    )
    
    assert response.status_code == 415
    assert "Unsupported audio format" in response.json()["detail"]

def test_transcribe_audio_no_file(client, test_user, auth_headers):
    """Test transcription without providing a file."""
    response = client.post(
        "/api/v1/transcription/transcribe",
        headers=auth_headers
    )
    
    assert response.status_code == 422  # Validation error

def test_transcribe_audio_too_long(client, test_user, auth_headers):
    """Test transcription with audio that's too long."""
    audio_content = b"fake_audio_content"
    
    with patch('app.services.transcription_service.transcription_service') as mock_service:
        mock_service.is_available.return_value = True
        mock_service.transcribe_audio.side_effect = ValueError("Audio duration (65.0s) exceeds maximum allowed (60s)")
        
        response = client.post(
            "/api/v1/transcription/transcribe",
            headers=auth_headers,
            files={"audio_file": ("test.wav", BytesIO(audio_content), "audio/wav")}
        )
        
        assert response.status_code == 400
        assert "exceeds maximum allowed" in response.json()["detail"]

def test_transcribe_audio_unauthorized(client):
    """Test transcription without authentication."""
    audio_content = b"fake_audio_content"
    
    response = client.post(
        "/api/v1/transcription/transcribe",
        files={"audio_file": ("test.wav", BytesIO(audio_content), "audio/wav")}
    )
    
    assert response.status_code == 401

def test_get_supported_formats(client, test_user, auth_headers):
    """Test getting supported audio formats."""
    response = client.get("/api/v1/transcription/supported-formats", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert "audio/wav" in data
    assert "audio/mp3" in data

def test_get_service_status(client, test_user, auth_headers):
    """Test getting transcription service status."""
    with patch('app.services.transcription_service.transcription_service') as mock_service:
        mock_service.is_available.return_value = True
        
        response = client.get("/api/v1/transcription/service-status", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["available"] is True
        assert data["model"] == "whisper-base"
        assert data["max_duration_seconds"] == 60
        assert data["primary_language"] == "es"
        assert "supported_formats" in data

def test_transcription_service_initialization():
    """Test transcription service initialization."""
    from app.services.transcription_service import TranscriptionService
    
    with patch('whisper.load_model') as mock_load:
        mock_model = MagicMock()
        mock_load.return_value = mock_model
        
        service = TranscriptionService()
        assert service.is_available() is True
        mock_load.assert_called_once_with("base")

def test_transcription_service_model_load_failure():
    """Test transcription service when model loading fails."""
    from app.services.transcription_service import TranscriptionService
    
    with patch('whisper.load_model') as mock_load:
        mock_load.side_effect = Exception("Model loading failed")
        
        service = TranscriptionService()
        assert service.is_available() is False

@pytest.mark.asyncio
async def test_audio_duration_calculation():
    """Test audio duration calculation."""
    from app.services.transcription_service import TranscriptionService
    
    service = TranscriptionService()
    
    with patch('librosa.get_duration') as mock_duration:
        mock_duration.return_value = 30.5
        
        duration = await service._get_audio_duration("fake_path.wav")
        assert duration == 30.5

@pytest.mark.asyncio
async def test_audio_preprocessing():
    """Test audio preprocessing."""
    from app.services.transcription_service import TranscriptionService
    
    service = TranscriptionService()
    
    with patch('librosa.load') as mock_load, \
         patch('soundfile.write') as mock_write, \
         patch('tempfile.NamedTemporaryFile') as mock_temp:
        
        # Mock audio data
        mock_load.return_value = ([0.1, 0.2, 0.3], 16000)
        mock_temp.return_value.__enter__.return_value.name = "/tmp/test.wav"
        
        result_path = await service._preprocess_audio("input.mp3")
        
        mock_load.assert_called_once_with("input.mp3", sr=16000, mono=True)
        assert result_path == "/tmp/test.wav"