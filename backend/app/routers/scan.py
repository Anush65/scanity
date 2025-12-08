"""
Scan operations router
"""
import asyncio
import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse
import httpx

from ..models.scan import ScanRequest, ScanResult, ScanResponse
from ..models.response import ErrorResponse
from ..services.scanner import ScannerService
from ..services.analyzer import AnalyzerService
from ..services.ai_engine import AIEngine
from ..services.report_generator import ReportGenerator
from ..utils.validators import validate_url, sanitize_scan_options
from ..utils.helpers import calculate_health_score
from ..config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/scan", tags=["scan"])

# In-memory storage for scan results (in production, use a database)
scan_storage: Dict[str, Dict[str, Any]] = {}


async def get_scan_results(scan_id: str) -> Dict[str, Any]:
    """Get scan results from storage"""
    if scan_id not in scan_storage:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan_storage[scan_id]


@router.post("/", response_model=ScanResponse, status_code=202)
async def initiate_scan(
    scan_request: ScanRequest,
    background_tasks: BackgroundTasks
) -> ScanResponse:
    """
    Initiate a new website scan
    """
    # Validate URL
    is_valid, error_message = validate_url(str(scan_request.url))
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)

    # Sanitize scan options
    sanitized_options = sanitize_scan_options(scan_request.options or {})

    # Create scan result entry
    from ..models.scan import ScanResult
    from datetime import datetime
    import uuid

    scan_id = str(uuid.uuid4())

    # Initialize scan result
    scan_result = ScanResult(
        scan_id=scan_id,
        url=str(scan_request.url),
        status="pending"
    )

    # Store initial result
    scan_storage[scan_id] = scan_result.dict()

    # Add background task to perform scan
    background_tasks.add_task(
        perform_scan_task,
        scan_id,
        str(scan_request.url),
        sanitized_options
    )

    return ScanResponse(
        scan_id=scan_id,
        status="pending",
        estimated_time=30
    )


@router.get("/{scan_id}", response_model=ScanResult)
async def get_scan_status(scan_id: str) -> ScanResult:
    """
    Get scan results by ID
    """
    try:
        scan_data = await get_scan_results(scan_id)
        return ScanResult(**scan_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting scan status: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{scan_id}/pdf")
async def download_pdf_report(scan_id: str) -> StreamingResponse:
    """
    Download PDF report for a scan
    """
    try:
        scan_data = await get_scan_results(scan_id)

        if scan_data.get("status") != "completed":
            raise HTTPException(status_code=400, detail="Scan not completed")

        # Generate PDF
        report_generator = ReportGenerator()
        pdf_bytes = await report_generator.generate_pdf_report(
            scan_data,
            scan_data.get("screenshot_url")
        )

        if not pdf_bytes:
            raise HTTPException(status_code=500, detail="Failed to generate PDF")

        # Return PDF as streaming response
        return StreamingResponse(
            iter([pdf_bytes]),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=scanity-report-{scan_id}.pdf"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate PDF report")


async def perform_scan_task(scan_id: str, url: str, options: Dict[str, Any]):
    """
    Background task to perform website scanning
    """
    try:
        logger.info(f"Starting scan {scan_id} for {url}")

        # Update status to scanning
        if scan_id in scan_storage:
            scan_storage[scan_id]["status"] = "scanning"

        # Initialize services
        async with ScannerService() as scanner, AIEngine() as ai_engine:
            # Perform scan
            scan_data = await scanner.scan_website(url, options)

            # Analyze scan results
            analyzer = AnalyzerService()
            analysis_results = analyzer.analyze_scan_data(scan_data)

            # Enhance with AI recommendations
            categories = analysis_results.get("categories", {})
            all_issues = []

            for category_name, category_result in categories.items():
                all_issues.extend(category_result.get("issues", []))

            enhanced_issues = await ai_engine.enhance_issues_with_ai(all_issues, url)

            # Update categories with enhanced issues
            for category_name, category_result in categories.items():
                category_issues = [
                    issue for issue in enhanced_issues
                    if issue.category == category_name
                ]
                category_result["issues"] = [issue.dict() for issue in category_issues]

            # Generate AI summary
            ai_summary = await ai_engine.generate_website_summary(analysis_results, url)

            # Calculate overall health score
            health_score = calculate_health_score(categories)

            # Prepare final result
            final_result = {
                "scan_id": scan_id,
                "url": url,
                "status": "completed",
                "health_score": health_score,
                "categories": categories,
                "metrics": analysis_results.get("metrics"),
                "screenshot_url": scan_data.get("screenshot"),
                "ai_summary": ai_summary,
                "scan_duration": scan_data.get("scan_duration", 0),
                "created_at": scan_storage[scan_id].get("created_at")
            }

            # Store final result
            scan_storage[scan_id] = final_result

            logger.info(f"Scan {scan_id} completed successfully")

    except Exception as e:
        logger.error(f"Scan {scan_id} failed: {str(e)}")

        # Update status to failed
        if scan_id in scan_storage:
            scan_storage[scan_id].update({
                "status": "failed",
                "error_message": str(e)
            })


@router.delete("/{scan_id}")
async def delete_scan(scan_id: str) -> Dict[str, str]:
    """
    Delete scan results (for cleanup)
    """
    try:
        if scan_id not in scan_storage:
            raise HTTPException(status_code=404, detail="Scan not found")

        del scan_storage[scan_id]
        return {"message": f"Scan {scan_id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting scan: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete scan")


@router.get("/")
async def list_scans() -> Dict[str, Any]:
    """
    List all scans (for testing/monitoring)
    """
    try:
        scans = []
        for scan_id, scan_data in scan_storage.items():
            scans.append({
                "scan_id": scan_id,
                "url": scan_data.get("url"),
                "status": scan_data.get("status"),
                "health_score": scan_data.get("health_score"),
                "created_at": scan_data.get("created_at")
            })

        return {"scans": scans, "total": len(scans)}

    except Exception as e:
        logger.error(f"Error listing scans: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list scans")