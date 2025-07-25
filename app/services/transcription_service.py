import whisper
import tempfile
import os
import logging
from typing import Dict, Any, Optional
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError
import librosa
import soundfile as sf

class TranscriptionService:
    def __init__(self):
        """Initialize the transcription service with Whisper model."""
        try:
            # Load the base (light) model for faster processing
            self.model = whisper.load_model("base")
            logging.info("Whisper model loaded successfully")
        except Exception as e:
            logging.error(f"Failed to load Whisper model: {e}")
            self.model = None
    
    async def transcribe_audio(
        self, 
        audio_file_path: str, 
        max_duration: int = 60,
        language: str = "es"
    ) -> Dict[str, Any]:
        """
        Transcribe audio file to text using Whisper.
        
        Args:
            audio_file_path: Path to the audio file
            max_duration: Maximum allowed duration in seconds
            language: Target language for transcription (default: Spanish)
            
        Returns:
            Dictionary containing transcription results
            
        Raises:
            ValueError: If audio is too long or invalid
            RuntimeError: If transcription fails
        """
        if not self.model:
            raise RuntimeError("Whisper model not available")
        
        try:
            # Validate audio duration
            duration = await self._get_audio_duration(audio_file_path)
            if duration > max_duration:
                raise ValueError(f"Audio duration ({duration:.1f}s) exceeds maximum allowed ({max_duration}s)")
            
            # Preprocess audio if needed
            processed_audio_path = await self._preprocess_audio(audio_file_path)
            
            # Transcribe using Whisper
            result = self.model.transcribe(
                processed_audio_path,
                language=language,
                task="transcribe",
                fp16=False,  # Use fp32 for better compatibility
                verbose=False
            )
            
            # Clean up processed file if it's different from original
            if processed_audio_path != audio_file_path:
                os.unlink(processed_audio_path)
            
            return {
                "text": result["text"].strip(),
                "language": result.get("language", language),
                "duration": duration,
                "confidence": self._calculate_confidence(result)
            }
            
        except Exception as e:
            logging.error(f"Transcription failed: {e}")
            raise RuntimeError(f"Transcription failed: {str(e)}")
    
    async def _get_audio_duration(self, audio_file_path: str) -> float:
        """Get duration of audio file in seconds."""
        try:
            # Try with librosa first (more reliable)
            duration = librosa.get_duration(path=audio_file_path)
            return duration
        except Exception:
            try:
                # Fallback to pydub
                audio = AudioSegment.from_file(audio_file_path)
                return len(audio) / 1000.0  # Convert ms to seconds
            except Exception as e:
                raise ValueError(f"Could not determine audio duration: {e}")
    
    async def _preprocess_audio(self, audio_file_path: str) -> str:
        """
        Preprocess audio file for better transcription.
        Converts to WAV format and ensures proper sample rate.
        """
        try:
            # Load audio with librosa (handles various formats)
            audio_data, sample_rate = librosa.load(
                audio_file_path, 
                sr=16000,  # Whisper works best with 16kHz
                mono=True   # Convert to mono
            )
            
            # Create temporary file for processed audio
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Save processed audio
            sf.write(temp_path, audio_data, 16000)
            
            return temp_path
            
        except Exception as e:
            logging.warning(f"Audio preprocessing failed, using original file: {e}")
            return audio_file_path
    
    def _calculate_confidence(self, whisper_result: Dict[str, Any]) -> Optional[float]:
        """
        Calculate average confidence score from Whisper segments.
        """
        try:
            segments = whisper_result.get("segments", [])
            if not segments:
                return None
            
            # Calculate average confidence from all segments
            total_confidence = 0
            total_duration = 0
            
            for segment in segments:
                if "avg_logprob" in segment and "end" in segment and "start" in segment:
                    # Convert log probability to confidence (approximate)
                    confidence = min(1.0, max(0.0, (segment["avg_logprob"] + 1.0)))
                    duration = segment["end"] - segment["start"]
                    
                    total_confidence += confidence * duration
                    total_duration += duration
            
            if total_duration > 0:
                return total_confidence / total_duration
            
            return None
            
        except Exception:
            return None
    
    def is_available(self) -> bool:
        """Check if the transcription service is available."""
        return self.model is not None

# Global instance
transcription_service = TranscriptionService()