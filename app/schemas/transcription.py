from pydantic import BaseModel, Field
from typing import Optional

class TranscriptionResponse(BaseModel):
    text: str = Field(..., description="Transcribed text from audio")
    language: str = Field(..., description="Detected language of the audio")
    duration: float = Field(..., description="Duration of the audio file in seconds")
    confidence: Optional[float] = Field(None, description="Confidence score of transcription")
    
class TranscriptionError(BaseModel):
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")