"""
API response models
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    ollama_status: str = Field(..., description="Ollama service status")
    version: str = Field(..., description="Application version")
    timestamp: Optional[str] = Field(None, description="Health check timestamp")


class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = Field(default=False, description="Success flag")
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


class SuccessResponse(BaseModel):
    """Standard success response"""
    success: bool = Field(default=True, description="Success flag")
    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")