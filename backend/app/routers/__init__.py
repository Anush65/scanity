"""
API routers for the Scanity application
"""
from .scan import router as scan_router
from .health import router as health_router

__all__ = ["scan_router", "health_router"]