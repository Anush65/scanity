"""
Health check router
"""
from fastapi import APIRouter, Depends
from typing import Dict
import httpx
import logging

from ..models.response import HealthResponse
from ..services.ai_engine import AIEngine
from ..config import settings
from .. import __version__

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("/", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Comprehensive health check endpoint
    """
    from datetime import datetime

    # Check Ollama service
    ollama_status = "disconnected"
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(f"{settings.ollama_host}/api/tags")
            if response.status_code == 200:
                ollama_status = "connected"
            else:
                ollama_status = "error"
    except Exception as e:
        logger.debug(f"Ollama health check failed: {str(e)}")
        ollama_status = "disconnected"

    return HealthResponse(
        status="healthy",
        ollama_status=ollama_status,
        version=__version__,
        timestamp=datetime.utcnow().isoformat()
    )


@router.get("/simple")
async def simple_health() -> Dict[str, str]:
    """
    Simple health check for monitoring systems
    """
    return {"status": "ok", "service": "scanity-backend"}