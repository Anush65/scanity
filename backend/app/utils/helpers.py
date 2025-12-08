"""
Helper utilities for the Scanity application
"""
import uuid
import math
from typing import Dict, List, Literal
from ..models.scan import CategoryResult, Issue


def generate_scan_id() -> str:
    """Generate a unique scan ID"""
    return str(uuid.uuid4())


def calculate_health_score(categories: Dict[str, CategoryResult]) -> int:
    """
    Calculate overall health score from category scores

    Args:
        categories: Dictionary of category results

    Returns:
        Overall health score (0-100)
    """
    if not categories:
        return 0

    # Weight categories differently
    weights = {
        "security": 0.4,  # Security is most important
        "performance": 0.35,  # Performance is second
        "quality": 0.25  # Code quality is third
    }

    total_weighted_score = 0
    total_weight = 0

    for category_name, category_result in categories.items():
        weight = weights.get(category_name, 0.33)
        total_weighted_score += category_result.score * weight
        total_weight += weight

    if total_weight == 0:
        return 0

    return round(total_weighted_score / total_weight)


def get_severity_weight(severity: str) -> float:
    """
    Get numerical weight for issue severity

    Args:
        severity: Issue severity level

    Returns:
        Numerical weight (1.0-3.0)
    """
    severity_weights = {
        "LOW": 1.0,
        "MEDIUM": 2.0,
        "HIGH": 3.0
    }
    return severity_weights.get(severity, 1.0)


def get_severity_color(severity: str) -> str:
    """
    Get color code for issue severity

    Args:
        severity: Issue severity level

    Returns:
        Hex color code
    """
    severity_colors = {
        "LOW": "#10b981",      # Green
        "MEDIUM": "#f59e0b",   # Yellow/Orange
        "HIGH": "#dc2626"      # Red
    }
    return severity_colors.get(severity, "#6b7280")  # Gray for unknown


def get_score_color(score: int) -> str:
    """
    Get color code for health score

    Args:
        score: Health score (0-100)

    Returns:
        Hex color code
    """
    if score >= 90:
        return "#10b981"  # Green
    elif score >= 70:
        return "#f59e0b"  # Yellow/Orange
    else:
        return "#dc2626"  # Red


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human readable string

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string
    """
    if seconds < 1:
        return f"{int(seconds * 1000)}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    else:
        minutes = int(seconds // 60)
        remaining_seconds = int(seconds % 60)
        return f"{minutes}m {remaining_seconds}s"


def format_file_size(size_kb: int) -> str:
    """
    Format file size in KB to human readable string

    Args:
        size_kb: Size in kilobytes

    Returns:
        Formatted size string
    """
    if size_kb < 1024:
        return f"{size_kb}KB"
    elif size_kb < 1024 * 1024:
        return f"{size_kb / 1024:.1f}MB"
    else:
        return f"{size_kb / (1024 * 1024):.1f}GB"


def create_mock_issue(
    category: Literal["security", "performance", "quality"],
    severity: Literal["HIGH", "MEDIUM", "LOW"],
    title: str,
    description: str,
    impact: str,
    fix_steps: List[str],
    estimated_time: str = "5-15 minutes"
) -> Issue:
    """
    Create a mock issue for testing/fallback purposes

    Args:
        category: Issue category
        severity: Issue severity
        title: Issue title
        description: Issue description
        impact: Impact description
        fix_steps: List of fix steps
        estimated_time: Estimated time to fix

    Returns:
        Issue object
    """
    return Issue(
        category=category,
        severity=severity,
        title=title,
        description=description,
        impact=impact,
        fix_steps=fix_steps,
        estimated_time=estimated_time
    )


def merge_similar_issues(issues: List[Issue], similarity_threshold: float = 0.8) -> List[Issue]:
    """
    Merge similar issues to reduce duplicates

    Args:
        issues: List of issues to merge
        similarity_threshold: Threshold for considering issues similar

    Returns:
        List of merged issues
    """
    # Simple implementation based on title similarity
    merged_issues = []
    seen_titles = set()

    for issue in issues:
        # Check if similar title already exists
        title_lower = issue.title.lower()
        is_duplicate = False

        for seen_title in seen_titles:
            # Simple similarity check - you could make this more sophisticated
            if title_lower == seen_title.lower():
                is_duplicate = True
                break

        if not is_duplicate:
            merged_issues.append(issue)
            seen_titles.add(issue.title)

    return merged_issues