"""
PDF report generation service
"""
import logging
import os
import base64
from datetime import datetime
from typing import Dict, Any, Optional
from io import BytesIO

try:
    from weasyprint import HTML, CSS
    from jinja2 import Template
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("WeasyPrint not available, PDF generation will be disabled")

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Service for generating PDF reports from scan results"""

    def __init__(self):
        self.template_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
        self._ensure_template_directory()

    def _ensure_template_directory(self):
        """Ensure template directory exists"""
        if not os.path.exists(self.template_dir):
            os.makedirs(self.template_dir)

    async def generate_pdf_report(self, scan_results: Dict[str, Any], screenshot_data: Optional[str] = None) -> Optional[bytes]:
        """
        Generate a PDF report from scan results

        Args:
            scan_results: Complete scan results
            screenshot_data: Base64 encoded screenshot data

        Returns:
            PDF file as bytes, or None if generation fails
        """
        if not WEASYPRINT_AVAILABLE:
            logger.error("WeasyPrint not available for PDF generation")
            return None

        try:
            # Prepare report data
            report_data = self._prepare_report_data(scan_results, screenshot_data)

            # Generate HTML from template
            html_content = self._render_html_template(report_data)

            # Convert HTML to PDF
            pdf_bytes = self._convert_html_to_pdf(html_content)

            return pdf_bytes

        except Exception as e:
            logger.error(f"Error generating PDF report: {str(e)}")
            return None

    def _prepare_report_data(self, scan_results: Dict[str, Any], screenshot_data: Optional[str] = None) -> Dict[str, Any]:
        """Prepare data for the PDF template"""
        current_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")

        # Extract basic information
        url = scan_results.get("url", "Unknown URL")
        scan_id = scan_results.get("scan_id", "Unknown")
        health_score = scan_results.get("health_score", 0)
        categories = scan_results.get("categories", {})
        metrics = scan_results.get("metrics", {})
        ai_summary = scan_results.get("ai_summary", {})

        # Process security issues
        security_data = categories.get("security", {})
        security_issues = security_data.get("issues", [])
        security_score = security_data.get("score", 0)

        # Process performance issues
        performance_data = categories.get("performance", {})
        performance_issues = performance_data.get("issues", [])
        performance_score = performance_data.get("score", 0)

        # Process quality issues
        quality_data = categories.get("quality", {})
        quality_issues = quality_data.get("issues", [])
        quality_score = quality_data.get("score", 0)

        # Get severity counts
        severity_counts = self._count_issues_by_severity(security_issues + performance_issues + quality_issues)

        # Process screenshot
        screenshot_src = ""
        if screenshot_data:
            # Convert base64 to data URL for HTML
            if screenshot_data.startswith("data:image/"):
                screenshot_src = screenshot_data
            else:
                screenshot_src = f"data:image/png;base64,{screenshot_data}"

        return {
            "report_title": "Website Security & Performance Audit Report",
            "url": url,
            "scan_id": scan_id,
            "generated_date": current_time,
            "health_score": health_score,
            "health_score_color": self._get_score_color(health_score),
            "screenshot_src": screenshot_src,
            "security": {
                "score": security_score,
                "score_color": self._get_score_color(security_score),
                "issues": security_issues,
                "issues_count": len(security_issues)
            },
            "performance": {
                "score": performance_score,
                "score_color": self._get_score_color(performance_score),
                "issues": performance_issues,
                "issues_count": len(performance_issues),
                "metrics": metrics
            },
            "quality": {
                "score": quality_score,
                "score_color": self._get_score_color(quality_score),
                "issues": quality_issues,
                "issues_count": len(quality_issues)
            },
            "severity_counts": severity_counts,
            "ai_summary": ai_summary,
            "total_issues": len(security_issues) + len(performance_issues) + len(quality_issues)
        }

    def _render_html_template(self, report_data: Dict[str, Any]) -> str:
        """Render HTML template with report data"""
        template_str = self._get_pdf_template()
        template = Template(template_str)
        return template.render(**report_data)

    def _convert_html_to_pdf(self, html_content: str) -> bytes:
        """Convert HTML content to PDF using WeasyPrint"""
        # CSS styles for the PDF
        css_styles = CSS(string=self._get_pdf_css())

        # Create HTML object and convert to PDF
        html = HTML(string=html_content)
        pdf_buffer = BytesIO()
        html.write_pdf(pdf_buffer, stylesheets=[css_styles])
        pdf_buffer.seek(0)

        return pdf_buffer.read()

    def _count_issues_by_severity(self, issues: list) -> Dict[str, int]:
        """Count issues by severity level"""
        counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for issue in issues:
            severity = issue.get("severity", "LOW")
            if severity in counts:
                counts[severity] += 1
        return counts

    def _get_score_color(self, score: int) -> str:
        """Get color code for score"""
        if score >= 90:
            return "#10b981"  # Green
        elif score >= 70:
            return "#f59e0b"  # Yellow/Orange
        else:
            return "#dc2626"  # Red

    def _get_pdf_template(self) -> str:
        """Get the HTML template for PDF generation"""
        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{{ report_title }}</title>
    <style>
        /* CSS will be added separately */
    </style>
</head>
<body>
    <div class="document">
        <!-- Header -->
        <header class="header">
            <div class="logo">
                <h1>Scanity</h1>
                <p>Website Security & Performance Audit</p>
            </div>
            <div class="report-info">
                <p><strong>Website:</strong> {{ url }}</p>
                <p><strong>Report Date:</strong> {{ generated_date }}</p>
                <p><strong>Scan ID:</strong> {{ scan_id }}</p>
            </div>
        </header>

        <!-- Executive Summary -->
        <section class="executive-summary">
            <h2>Executive Summary</h2>

            <div class="health-score-section">
                <div class="score-circle" style="border-color: {{ health_score_color }}; color: {{ health_score_color }};">
                    <div class="score-number">{{ health_score }}</div>
                    <div class="score-label">Overall Score</div>
                </div>
                <div class="summary-text">
                    {% if ai_summary.summary %}
                        <p>{{ ai_summary.summary }}</p>
                        <p><strong>Status:</strong> {{ ai_summary.overall_status or 'Good' }}</p>
                    {% else %}
                        <p>Your website has received a health score of {{ health_score }}/100.</p>
                        <p>{% if health_score >= 90 %}Excellent condition with minimal issues.{% elif health_score >= 70 %}Good condition with some improvement areas.{% elif health_score >= 50 %}Fair condition with several issues to address.{% else %}Poor condition requiring immediate attention.{% endif %}</p>
                    {% endif %}
                </div>
            </div>

            <div class="stats-grid">
                <div class="stat-card">
                    <h3>Total Issues</h3>
                    <div class="stat-number">{{ total_issues }}</div>
                </div>
                <div class="stat-card high-severity">
                    <h3>High Priority</h3>
                    <div class="stat-number">{{ severity_counts.HIGH }}</div>
                </div>
                <div class="stat-card medium-severity">
                    <h3>Medium Priority</h3>
                    <div class="stat-number">{{ severity_counts.MEDIUM }}</div>
                </div>
                <div class="stat-card low-severity">
                    <h3>Low Priority</h3>
                    <div class="stat-number">{{ severity_counts.LOW }}</div>
                </div>
            </div>
        </section>

        {% if screenshot_src %}
        <!-- Screenshot -->
        <section class="screenshot-section">
            <h2>Website Screenshot</h2>
            <div class="screenshot-container">
                <img src="{{ screenshot_src }}" alt="Website Screenshot" />
            </div>
        </section>
        {% endif %}

        <!-- Security Analysis -->
        <section class="category-section">
            <h2>Security Analysis</h2>
            <div class="category-header">
                <div class="category-score" style="color: {{ security.score_color }};">
                    {{ security.score }}/100
                </div>
                <div class="category-summary">
                    {{ security.issues_count }} security issue{{ 's' if security.issues_count != 1 else '' }} found
                </div>
            </div>

            {% if security.issues %}
                {% for issue in security.issues %}
                <div class="issue-card severity-{{ issue.severity.lower() }}">
                    <h3>{{ issue.title }}</h3>
                    <div class="issue-meta">
                        <span class="severity-badge severity-{{ issue.severity.lower() }}">{{ issue.severity }}</span>
                        <span class="time-estimate">{{ issue.estimated_time }}</span>
                    </div>
                    <div class="issue-description">{{ issue.description }}</div>
                    {% if issue.impact %}
                    <div class="issue-impact">
                        <strong>Impact:</strong> {{ issue.impact }}
                    </div>
                    {% endif %}
                    {% if issue.fix_steps %}
                    <div class="issue-fix-steps">
                        <strong>Fix Steps:</strong>
                        <ol>
                            {% for step in issue.fix_steps %}
                            <li>{{ step }}</li>
                            {% endfor %}
                        </ol>
                    </div>
                    {% endif %}
                </div>
                {% endfor %}
            {% else %}
                <p class="no-issues">No security issues detected. Great job!</p>
            {% endif %}
        </section>

        <!-- Performance Analysis -->
        <section class="category-section">
            <h2>Performance Analysis</h2>
            <div class="category-header">
                <div class="category-score" style="color: {{ performance.score_color }};">
                    {{ performance.score }}/100
                </div>
                <div class="category-summary">
                    {{ performance.issues_count }} performance issue{{ 's' if performance.issues_count != 1 else '' }} found
                </div>
            </div>

            {% if performance.metrics %}
            <div class="metrics-grid">
                <div class="metric-card">
                    <h4>Page Load Time</h4>
                    <div class="metric-value">{{ "%.1f"|format(performance.metrics.page_load_time) }}s</div>
                </div>
                <div class="metric-card">
                    <h4>Total Size</h4>
                    <div class="metric-value">{{ performance.metrics.total_size_kb }}KB</div>
                </div>
                <div class="metric-card">
                    <h4>Requests</h4>
                    <div class="metric-value">{{ performance.metrics.requests_count }}</div>
                </div>
            </div>
            {% endif %}

            {% if performance.issues %}
                {% for issue in performance.issues %}
                <div class="issue-card severity-{{ issue.severity.lower() }}">
                    <h3>{{ issue.title }}</h3>
                    <div class="issue-meta">
                        <span class="severity-badge severity-{{ issue.severity.lower() }}">{{ issue.severity }}</span>
                        <span class="time-estimate">{{ issue.estimated_time }}</span>
                    </div>
                    <div class="issue-description">{{ issue.description }}</div>
                    {% if issue.impact %}
                    <div class="issue-impact">
                        <strong>Impact:</strong> {{ issue.impact }}
                    </div>
                    {% endif %}
                    {% if issue.fix_steps %}
                    <div class="issue-fix-steps">
                        <strong>Fix Steps:</strong>
                        <ol>
                            {% for step in issue.fix_steps %}
                            <li>{{ step }}</li>
                            {% endfor %}
                        </ol>
                    </div>
                    {% endif %}
                </div>
                {% endfor %}
            {% else %}
                <p class="no-issues">No performance issues detected. Excellent!</p>
            {% endif %}
        </section>

        <!-- Code Quality Analysis -->
        <section class="category-section">
            <h2>Code Quality Analysis</h2>
            <div class="category-header">
                <div class="category-score" style="color: {{ quality.score_color }};">
                    {{ quality.score }}/100
                </div>
                <div class="category-summary">
                    {{ quality.issues_count }} quality issue{{ 's' if quality.issues_count != 1 else '' }} found
                </div>
            </div>

            {% if quality.issues %}
                {% for issue in quality.issues %}
                <div class="issue-card severity-{{ issue.severity.lower() }}">
                    <h3>{{ issue.title }}</h3>
                    <div class="issue-meta">
                        <span class="severity-badge severity-{{ issue.severity.lower() }}">{{ issue.severity }}</span>
                        <span class="time-estimate">{{ issue.estimated_time }}</span>
                    </div>
                    <div class="issue-description">{{ issue.description }}</div>
                    {% if issue.impact %}
                    <div class="issue-impact">
                        <strong>Impact:</strong> {{ issue.impact }}
                    </div>
                    {% endif %}
                    {% if issue.fix_steps %}
                    <div class="issue-fix-steps">
                        <strong>Fix Steps:</strong>
                        <ol>
                            {% for step in issue.fix_steps %}
                            <li>{{ step }}</li>
                            {% endfor %}
                        </ol>
                    </div>
                    {% endif %}
                </div>
                {% endfor %}
            {% else %}
                <p class="no-issues">No code quality issues detected. Well done!</p>
            {% endif %}
        </section>

        <!-- Recommendations -->
        {% if ai_summary.recommendations %}
        <section class="recommendations-section">
            <h2>Recommendations</h2>
            {% for rec in ai_summary.recommendations %}
            <div class="recommendation-card priority-{{ rec.priority.lower() }}">
                <h3>{{ rec.action }}</h3>
                <div class="recommendation-meta">
                    <span class="priority-badge priority-{{ rec.priority.lower() }}">{{ rec.priority }} Priority</span>
                </div>
                <p>{{ rec.reason }}</p>
            </div>
            {% endfor %}
        </section>
        {% endif %}

        <!-- Next Steps -->
        {% if ai_summary.next_steps %}
        <section class="next-steps-section">
            <h2>Next Steps</h2>
            <ol>
                {% for step in ai_summary.next_steps %}
                <li>{{ step }}</li>
                {% endfor %}
            </ol>
        </section>
        {% endif %}

        <!-- Footer -->
        <footer class="footer">
            <p>Generated by Scanity - Website Security & Performance Auditor</p>
            <p>Report generated on {{ generated_date }}</p>
        </footer>
    </div>
</body>
</html>
        """

    def _get_pdf_css(self) -> str:
        """Get CSS styles for the PDF"""
        return """
        @page {
            size: A4;
            margin: 2cm;
            @top-center {
                content: "Scanity Website Audit Report";
                font-size: 10pt;
                color: #666;
            }
            @bottom-center {
                content: "Page " counter(page);
                font-size: 10pt;
                color: #666;
            }
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-size: 12pt;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
        }

        .document {
            max-width: 100%;
        }

        .header {
            border-bottom: 3px solid #dc2626;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }

        .header::after {
            content: "";
            display: table;
            clear: both;
        }

        .logo {
            float: left;
        }

        .logo h1 {
            color: #dc2626;
            margin: 0;
            font-size: 28pt;
            font-weight: bold;
        }

        .logo p {
            margin: 5px 0 0 0;
            color: #666;
            font-size: 14pt;
        }

        .report-info {
            float: right;
            text-align: right;
        }

        .executive-summary {
            margin-bottom: 30px;
        }

        .health-score-section {
            display: flex;
            align-items: center;
            margin-bottom: 30px;
        }

        .score-circle {
            width: 120px;
            height: 120px;
            border: 4px solid #10b981;
            border-radius: 50%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            margin-right: 30px;
        }

        .score-number {
            font-size: 36pt;
            font-weight: bold;
            line-height: 1;
        }

        .score-label {
            font-size: 10pt;
            text-transform: uppercase;
        }

        .summary-text {
            flex: 1;
            font-size: 14pt;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-top: 20px;
        }

        .stat-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }

        .stat-card.high-severity {
            border-left: 4px solid #dc2626;
        }

        .stat-card.medium-severity {
            border-left: 4px solid #f59e0b;
        }

        .stat-card.low-severity {
            border-left: 4px solid #10b981;
        }

        .stat-card h3 {
            margin: 0 0 10px 0;
            font-size: 12pt;
            color: #666;
        }

        .stat-number {
            font-size: 24pt;
            font-weight: bold;
            color: #333;
        }

        .screenshot-section {
            margin-bottom: 30px;
            page-break-inside: avoid;
        }

        .screenshot-container {
            text-align: center;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            background: #f8f9fa;
        }

        .screenshot-container img {
            max-width: 100%;
            height: auto;
            border-radius: 4px;
        }

        .category-section {
            margin-bottom: 30px;
            page-break-inside: avoid;
        }

        .category-header {
            display: flex;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #eee;
        }

        .category-score {
            font-size: 36pt;
            font-weight: bold;
            margin-right: 20px;
        }

        .category-summary {
            font-size: 14pt;
            color: #666;
        }

        .issue-card {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
            page-break-inside: avoid;
        }

        .issue-card.severity-high {
            border-left: 5px solid #dc2626;
        }

        .issue-card.severity-medium {
            border-left: 5px solid #f59e0b;
        }

        .issue-card.severity-low {
            border-left: 5px solid #10b981;
        }

        .issue-card h3 {
            margin: 0 0 10px 0;
            font-size: 16pt;
            color: #333;
        }

        .issue-meta {
            display: flex;
            gap: 15px;
            margin-bottom: 15px;
        }

        .severity-badge {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 10pt;
            font-weight: bold;
            text-transform: uppercase;
        }

        .severity-badge.severity-high {
            background: #dc2626;
            color: white;
        }

        .severity-badge.severity-medium {
            background: #f59e0b;
            color: white;
        }

        .severity-badge.severity-low {
            background: #10b981;
            color: white;
        }

        .time-estimate {
            color: #666;
            font-size: 11pt;
        }

        .issue-description {
            margin-bottom: 15px;
        }

        .issue-impact {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 15px;
        }

        .issue-fix-steps ol {
            margin: 10px 0;
            padding-left: 20px;
        }

        .issue-fix-steps li {
            margin-bottom: 5px;
        }

        .no-issues {
            background: #d1fae5;
            color: #065f46;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            font-weight: bold;
        }

        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }

        .metric-card {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            text-align: center;
        }

        .metric-card h4 {
            margin: 0 0 5px 0;
            font-size: 11pt;
            color: #666;
        }

        .metric-value {
            font-size: 18pt;
            font-weight: bold;
            color: #333;
        }

        .recommendations-section {
            margin-bottom: 30px;
        }

        .recommendation-card {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
        }

        .recommendation-card.priority-high {
            border-left: 5px solid #dc2626;
        }

        .recommendation-card.priority-medium {
            border-left: 5px solid #f59e0b;
        }

        .recommendation-card.priority-low {
            border-left: 5px solid #10b981;
        }

        .recommendation-card h3 {
            margin: 0 0 10px 0;
            font-size: 16pt;
            color: #333;
        }

        .priority-badge {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 10pt;
            font-weight: bold;
            text-transform: uppercase;
        }

        .priority-badge.priority-high {
            background: #dc2626;
            color: white;
        }

        .priority-badge.priority-medium {
            background: #f59e0b;
            color: white;
        }

        .priority-badge.priority-low {
            background: #10b981;
            color: white;
        }

        .next-steps-section {
            margin-bottom: 30px;
        }

        .next-steps-section ol {
            padding-left: 20px;
        }

        .next-steps-section li {
            margin-bottom: 8px;
        }

        .footer {
            border-top: 1px solid #ddd;
            padding-top: 20px;
            margin-top: 40px;
            text-align: center;
            color: #666;
            font-size: 10pt;
        }

        h1, h2, h3, h4, h5, h6 {
            color: #1f2937;
        }

        h2 {
            font-size: 20pt;
            border-bottom: 2px solid #dc2626;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }

        a {
            color: #dc2626;
            text-decoration: none;
        }

        strong {
            color: #1f2937;
        }

        /* Print optimizations */
        @media print {
            body {
                font-size: 11pt;
            }

            .stats-grid {
                grid-template-columns: repeat(2, 1fr);
            }

            .metrics-grid {
                grid-template-columns: 1fr;
            }
        }
        """