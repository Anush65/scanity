"""
Data models for the Scanity application
"""
from .scan import ScanRequest, ScanResult, Issue, CategoryResult, PerformanceMetrics
from .response import HealthResponse, ErrorResponse

__all__ = [
    "ScanRequest",
    "ScanResult",
    "Issue",
    "CategoryResult",
    "PerformanceMetrics",
    "HealthResponse",
    "ErrorResponse"
]