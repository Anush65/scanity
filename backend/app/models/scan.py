"""
Scan-related data models
"""
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
import uuid


class ScanRequest(BaseModel):
    """Request model for initiating a scan"""
    url: HttpUrl = Field(..., description="Website URL to scan")
    options: Optional[Dict[str, Any]] = Field(
        default={
            "include_screenshot": True,
            "scan_depth": "standard",
            "mobile_view": False
        },
        description="Scanning options"
    )


class Issue(BaseModel):
    """Individual issue detected during scan"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category: Literal["security", "performance", "quality"] = Field(..., description="Issue category")
    severity: Literal["HIGH", "MEDIUM", "LOW"] = Field(..., description="Issue severity")
    title: str = Field(..., description="Issue title")
    description: str = Field(..., description="Issue description")
    impact: str = Field(..., description="Why this issue matters")
    fix_steps: List[str] = Field(..., description="Steps to fix the issue")
    estimated_time: str = Field(..., description="Estimated time to fix")
    code_example: Optional[str] = Field(None, description="Code example for fix")
    affected_resources: Optional[List[str]] = Field(None, description="Affected resources")


class CategoryResult(BaseModel):
    """Results for a specific category"""
    score: int = Field(..., ge=0, le=100, description="Category score (0-100)")
    issues_count: int = Field(..., ge=0, description="Number of issues found")
    issues: List[Issue] = Field(default_factory=list, description="List of issues")


class PerformanceMetrics(BaseModel):
    """Performance metrics from the scan"""
    page_load_time: float = Field(..., description="Page load time in seconds")
    total_size_kb: int = Field(..., description="Total page size in KB")
    requests_count: int = Field(..., description="Total number of requests")
    lcp: Optional[float] = Field(None, description="Largest Contentful Paint")
    fid: Optional[float] = Field(None, description="First Input Delay")
    cls: Optional[float] = Field(None, description="Cumulative Layout Shift")
    ttfb: Optional[float] = Field(None, description="Time to First Byte")


class ScanResult(BaseModel):
    """Complete scan result"""
    scan_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    url: str = Field(..., description="Scanned URL")
    status: Literal["pending", "completed", "failed"] = Field("pending", description="Scan status")
    health_score: Optional[int] = Field(None, ge=0, le=100, description="Overall health score")
    categories: Dict[str, CategoryResult] = Field(
        default_factory=lambda: {
            "security": CategoryResult(score=0, issues_count=0, issues=[]),
            "performance": CategoryResult(score=0, issues_count=0, issues=[]),
            "quality": CategoryResult(score=0, issues_count=0, issues=[])
        },
        description="Category-wise results"
    )
    metrics: Optional[PerformanceMetrics] = Field(None, description="Performance metrics")
    screenshot_url: Optional[str] = Field(None, description="URL to screenshot")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    error_message: Optional[str] = Field(None, description="Error message if scan failed")


class ScanResponse(BaseModel):
    """Response model for scan initiation"""
    scan_id: str = Field(..., description="Unique scan identifier")
    status: str = Field(default="pending", description="Initial scan status")
    estimated_time: int = Field(default=30, description="Estimated time in seconds")