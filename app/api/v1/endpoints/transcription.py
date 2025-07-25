from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File
from fastapi.responses import JSONResponse
import tempfile
import os
import logging
from typing import List

from app.core.dependencies import get_current_user
from app.models.models import User
from app.schemas.transcription import TranscriptionResponse, TranscriptionError
from app.services.transcription_service import transcription_service

router = APIRouter()

# Supported audio formats
SUPPORTED_FORMATS = {
    "audio/wav", "audio/wave", "audio/x-wav",
    "audio/mpeg", "audio/mp3", "audio/x-mp3",
    "audio/mp4", "audio/m4a", "audio/x-m4a",
    "audio/ogg", "audio/x-ogg",
    "audio/flac", "audio/x-flac",
    "audio/webm", "audio/x-webm"
}

# Maximum file size (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024

@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    current_user: User = Depends(get_current_user),
    audio_file: UploadFile = File(..., description="Audio file to transcribe (max 1 minute, 10MB)")
):
    """
    Transcribe audio file to Spanish text using Whisper
    
    - **audio_file**: Audio file in supported format (WAV, MP3, MP4, M4A, OGG, FLAC, WebM)
    - **Max duration**: 60 seconds
    - **Max file size**: 10MB
    - **Language**: Optimized for Spanish transcription
    
    Returns transcribed text with confidence score and metadata
    """
    try:
        # Check if transcription service is available
        if not transcription_service.is_available():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Transcription service is not available. Whisper model failed to load."
            )
        
        # Validate file
        if not audio_file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )
        
        # Check file size
        if audio_file.size and audio_file.size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size ({audio_file.size / 1024 / 1024:.1f}MB) exceeds maximum allowed (10MB)"
            )
        
        # Check content type
        if audio_file.content_type and audio_file.content_type not in SUPPORTED_FORMATS:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Unsupported audio format: {audio_file.content_type}. "
                       f"Supported formats: {', '.join(sorted(SUPPORTED_FORMATS))}"
            )
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{audio_file.filename}") as temp_file:
            temp_path = temp_file.name
            
            try:
                # Read and save uploaded file
                content = await audio_file.read()
                temp_file.write(content)
                temp_file.flush()
                
                # Transcribe audio
                result = await transcription_service.transcribe_audio(
                    temp_path,
                    max_duration=60,  # 1 minute limit
                    language="es"     # Spanish
                )
                
                logging.info(f"Successfully transcribed audio for user {current_user.id}")
                
                return TranscriptionResponse(
                    text=result["text"],
                    language=result["language"],
                    duration=result["duration"],
                    confidence=result.get("confidence")
                )
                
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_path)
                except Exception as e:
                    logging.warning(f"Failed to clean up temporary file {temp_path}: {e}")
        
    except HTTPException:
        raise
    except ValueError as e:
        # Handle validation errors (e.g., audio too long)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except RuntimeError as e:
        # Handle transcription errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transcription failed: {str(e)}"
        )
    except Exception as e:
        logging.error(f"Unexpected error in transcription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during transcription"
        )

@router.get("/supported-formats", response_model=List[str])
async def get_supported_formats():
    """
    Get list of supported audio formats for transcription
    
    Returns list of MIME types that are supported for audio transcription
    """
    return sorted(list(SUPPORTED_FORMATS))

@router.get("/service-status", response_model=dict)
async def get_service_status():
    """
    Check transcription service status
    
    Returns current status of the Whisper transcription service
    """
    is_available = transcription_service.is_available()
    
    return {
        "available": is_available,
        "model": "whisper-base" if is_available else None,
        "max_duration_seconds": 60,
        "max_file_size_mb": MAX_FILE_SIZE / 1024 / 1024,
        "primary_language": "es",
        "supported_formats": sorted(list(SUPPORTED_FORMATS))
    }