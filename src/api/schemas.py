from pydantic import BaseModel, Field
from typing import Optional, Dict


class HealthCheckResponse(BaseModel):
    """Health check response schema."""
    status: str = Field(..., description="Service status")
    model_loaded: bool = Field(..., description="Whether model is loaded")
    message: Optional[str] = Field(None, description="Additional message")


class PredictionRequest(BaseModel):
    """Request schema for prediction endpoint."""
    image_url: Optional[str] = Field(None, description="URL of image to predict")
    base64_image: Optional[str] = Field(None, description="Base64 encoded image")


class PredictionResponse(BaseModel):
    """Response schema for prediction endpoint."""
    class_name: str = Field(..., description="Predicted class")
    confidence: float = Field(..., description="Confidence score", ge=0, le=1)
    probabilities: Dict[str, float] = Field(..., description="Probabilities for each class")


class ErrorResponse(BaseModel):
    """Error response schema."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Error details")
