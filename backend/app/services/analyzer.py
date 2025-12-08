"""
Service for analyzing scan data and identifying issues
"""
import logging
from typing import Dict, List, Any, Optional
from ..models.scan import Issue, CategoryResult, PerformanceMetrics
from ..utils.helpers import create_mock_issue

logger = logging.getLogger(__name__)


class AnalyzerService:
    """Service for analyzing scan results and identifying issues"""

    def __init__(self):
        self.security_rules = self._init_security_rules()
        self.performance_rules = self._init_performance_rules()
        self.quality_rules = self._init_quality_rules()

    def analyze_scan_data(self, scan_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze raw scan data and identify issues

        Args:
            scan_data: Raw scan data from scanner

        Returns:
            Dictionary containing categorized issues and metrics
        """
        try:
            security_issues = self._analyze_security(scan_data.get("security", {}))
            performance_issues = self._analyze_performance(scan_data.get("performance", {}))
            quality_issues = self._analyze_quality(scan_data.get("quality", {}))

            # Calculate category results
            security_result = self._create_category_result(security_issues, "security")
            performance_result = self._create_category_result(performance_issues, "performance")
            quality_result = self._create_category_result(quality_issues, "quality")

            # Extract performance metrics
            metrics = self._extract_performance_metrics(scan_data.get("performance", {}))

            return {
                "categories": {
                    "security": security_result,
                    "performance": performance_result,
                    "quality": quality_result
                },
                "metrics": metrics,
                "raw_data": scan_data
            }

        except Exception as e:
            logger.error(f"Error analyzing scan data: {str(e)}")
            # Return empty results if analysis fails
            return {
                "categories": {
                    "security": CategoryResult(score=0, issues_count=0, issues=[]),
                    "performance": CategoryResult(score=0, issues_count=0, issues=[]),
                    "quality": CategoryResult(score=0, issues_count=0, issues=[])
                },
                "metrics": None,
                "raw_data": scan_data,
                "error": str(e)
            }

    def _analyze_security(self, security_data: Dict[str, Any]) -> List[Issue]:
        """Analyze security data and identify issues"""
        issues = []

        try:
            # Check security headers
            security_headers = security_data.get("security_headers", {})
            issues.extend(self._check_security_headers(security_headers))

            # Check for mixed content
            mixed_content = security_data.get("mixed_content", {})
            if mixed_content.get("hasMixedContent"):
                issues.append(create_mock_issue(
                    category="security",
                    severity="HIGH",
                    title="Mixed Content Detected",
                    description="Your HTTPS page is loading HTTP resources, which creates security vulnerabilities.",
                    impact="Mixed content can be blocked by browsers, causing functionality issues and potential security risks.",
                    fix_steps=[
                        "Update all HTTP resource URLs to HTTPS",
                        "Use protocol-relative URLs (//example.com/resource.js)",
                        "Test all functionality after updating URLs",
                        "Implement HSTS header to enforce HTTPS"
                    ],
                    estimated_time="15-30 minutes"
                ))

            # Check for exposed variables
            exposed_vars = security_data.get("exposed_variables", [])
            if exposed_vars:
                issues.append(create_mock_issue(
                    category="security",
                    severity="MEDIUM",
                    title="Sensitive JavaScript Variables Exposed",
                    description=f"Found {len(exposed_vars)} potentially sensitive JavaScript variables exposed in the global scope.",
                    impact="Exposed variables can leak sensitive information and be exploited by attackers.",
                    fix_steps=[
                        "Remove sensitive data from JavaScript global scope",
                        "Use environment variables for configuration",
                        "Implement proper access controls",
                        "Minimize variable scope using closures or modules"
                    ],
                    estimated_time="30-60 minutes"
                ))

        except Exception as e:
            logger.error(f"Error analyzing security data: {str(e)}")

        return issues

    def _check_security_headers(self, headers: Dict[str, Any]) -> List[Issue]:
        """Check for missing security headers"""
        issues = []

        # Define required security headers
        required_headers = {
            "content-security-policy": {
                "severity": "HIGH",
                "title": "Missing Content Security Policy (CSP)",
                "description": "CSP header is not set, which can prevent XSS attacks and data injection.",
                "impact": "Without CSP, your site is vulnerable to Cross-Site Scripting (XSS) attacks.",
                "fix_steps": [
                    "Implement a Content Security Policy header",
                    "Start with a restrictive policy and whitelist necessary domains",
                    "Use report-uri to monitor violations",
                    "Test thoroughly to avoid breaking functionality"
                ]
            },
            "x-frame-options": {
                "severity": "MEDIUM",
                "title": "Missing X-Frame-Options Header",
                "description": "X-Frame-Options header is not set, which can allow clickjacking attacks.",
                "impact": "Your site could be embedded in malicious iframes without your consent.",
                "fix_steps": [
                    "Add X-Frame-Options: DENY or SAMEORIGIN header",
                    "DENY prevents all framing",
                    "SAMEORIGIN allows framing by your own domain"
                ]
            },
            "strict-transport-security": {
                "severity": "HIGH",
                "title": "Missing HTTP Strict Transport Security (HSTS)",
                "description": "HSTS header is not set, which can lead to SSL stripping attacks.",
                "impact": "Users may access your site over HTTP, exposing them to man-in-the-middle attacks.",
                "fix_steps": [
                    "Add Strict-Transport-Security header with appropriate max-age",
                    "Start with a short max-age and increase gradually",
                    "Include subdomains if applicable",
                    "Consider preload submission for maximum security"
                ]
            },
            "x-content-type-options": {
                "severity": "MEDIUM",
                "title": "Missing X-Content-Type-Options Header",
                "description": "X-Content-Type-Options header is not set, which can lead to MIME sniffing attacks.",
                "impact": "Browsers might misinterpret content types, causing security issues.",
                "fix_steps": [
                    "Add X-Content-Type-Options: nosniff header",
                    "This prevents MIME type sniffing by browsers"
                ]
            },
            "referrer-policy": {
                "severity": "LOW",
                "title": "Missing Referrer-Policy Header",
                "description": "Referrer-Policy header is not set, which can leak sensitive information.",
                "impact": "Referrer information might be shared with third-party sites.",
                "fix_steps": [
                    "Add Referrer-Policy header (strict-origin-when-cross-origin recommended)",
                    "Choose appropriate policy based on your privacy requirements"
                ]
            }
        }

        for header_name, header_info in required_headers.items():
            if header_name not in headers or not headers[header_name]:
                issues.append(create_mock_issue(
                    category="security",
                    severity=header_info["severity"],
                    title=header_info["title"],
                    description=header_info["description"],
                    impact=header_info["impact"],
                    fix_steps=header_info["fix_steps"],
                    estimated_time="5-15 minutes"
                ))

        return issues

    def _analyze_performance(self, performance_data: Dict[str, Any]) -> List[Issue]:
        """Analyze performance data and identify issues"""
        issues = []

        try:
            timing = performance_data.get("timing", {})
            resources = performance_data.get("resources", {})
            web_vitals = performance_data.get("web_vitals", {})

            # Check page load time
            load_time = timing.get("loadComplete", 0) / 1000  # Convert to seconds
            if load_time > 5:
                issues.append(create_mock_issue(
                    category="performance",
                    severity="HIGH",
                    title="Slow Page Load Time",
                    description=f"Page takes {load_time:.1f} seconds to load, which is slower than recommended.",
                    impact="Slow load times increase bounce rates and hurt user experience.",
                    fix_steps=[
                        "Optimize images and use modern formats (WebP)",
                        "Minify CSS and JavaScript files",
                        "Enable browser caching",
                        "Use a Content Delivery Network (CDN)",
                        "Reduce server response time"
                    ],
                    estimated_time="1-2 hours"
                ))
            elif load_time > 3:
                issues.append(create_mock_issue(
                    category="performance",
                    severity="MEDIUM",
                    title="Moderate Page Load Time",
                    description=f"Page takes {load_time:.1f} seconds to load, which could be improved.",
                    impact="Faster load times improve user experience and conversion rates.",
                    fix_steps=[
                        "Optimize images and reduce file sizes",
                        "Minimize HTTP requests",
                        "Enable compression (gzip/brotli)",
                        "Optimize critical rendering path"
                    ],
                    estimated_time="30-60 minutes"
                ))

            # Check page size
            page_size = resources.get("totalSize", 0)
            if page_size > 3000:  # > 3MB
                issues.append(create_mock_issue(
                    category="performance",
                    severity="HIGH",
                    title="Large Page Size",
                    description=f"Page size is {page_size}KB, which is much larger than recommended.",
                    impact="Large pages load slowly and use more data, especially on mobile connections.",
                    fix_steps=[
                        "Compress images and use appropriate formats",
                        "Remove unused CSS and JavaScript",
                        "Lazy load images and videos",
                        "Use file compression",
                        "Consider splitting large pages"
                    ],
                    estimated_time="1-2 hours"
                ))

            # Check number of requests
            request_count = resources.get("totalRequests", 0)
            if request_count > 100:
                issues.append(create_mock_issue(
                    category="performance",
                    severity="MEDIUM",
                    title="Too Many HTTP Requests",
                    description=f"Page makes {request_count} HTTP requests, which can slow down loading.",
                    impact="More requests increase load time and server load.",
                    fix_steps=[
                        "Combine CSS and JavaScript files",
                        "Use CSS sprites for small images",
                        "Implement resource bundling",
                        "Use HTTP/2 or HTTP/3 if available"
                    ],
                    estimated_time="30-60 minutes"
                ))

            # Check Core Web Vitals
            lcp = web_vitals.get("lcp", 0) / 1000  # Convert to seconds
            if lcp > 4:
                issues.append(create_mock_issue(
                    category="performance",
                    severity="HIGH",
                    title="Poor Largest Contentful Paint (LCP)",
                    description=f"LCP is {lcp:.1f}s, which is much slower than the 2.5s recommended threshold.",
                    impact="Users perceive the page as slow, affecting user experience and SEO.",
                    fix_steps=[
                        "Optimize server response time",
                        "Use CDNs for static assets",
                        "Preload important resources",
                        "Optimize images and their delivery",
                        "Remove render-blocking JavaScript"
                    ],
                    estimated_time="1-2 hours"
                ))

        except Exception as e:
            logger.error(f"Error analyzing performance data: {str(e)}")

        return issues

    def _analyze_quality(self, quality_data: Dict[str, Any]) -> List[Issue]:
        """Analyze code quality and accessibility data"""
        issues = []

        try:
            html_structure = quality_data.get("html_structure", {})
            structure_issues = html_structure.get("issues", [])
            console_errors = quality_data.get("console_errors", [])

            # Process HTML structure issues
            for issue in structure_issues:
                issue_type = issue.get("type")

                if issue_type == "doctype":
                    issues.append(create_mock_issue(
                        category="quality",
                        severity="MEDIUM",
                        title="Missing DOCTYPE Declaration",
                        description="The HTML document is missing a DOCTYPE declaration.",
                        impact="Missing DOCTYPE can cause browsers to render in quirks mode, leading to inconsistent display.",
                        fix_steps=[
                            "Add <!DOCTYPE html> at the beginning of your HTML document",
                            "Validate your HTML after adding the DOCTYPE"
                        ],
                        estimated_time="5 minutes"
                    ))

                elif issue_type == "headings":
                    issues.append(create_mock_issue(
                        category="quality",
                        severity="MEDIUM",
                        title="No Heading Tags Found",
                        description="The page doesn't use any heading tags (h1-h6).",
                        impact="Headings improve readability and SEO. Without them, content structure is unclear.",
                        fix_steps=[
                            "Add appropriate heading tags to structure your content",
                            "Use h1 for the main page title",
                            "Use h2-h6 for subheadings in hierarchical order"
                        ],
                        estimated_time="15-30 minutes"
                    ))

                elif issue_type == "accessibility" and "alt text" in issue["message"]:
                    count = issue.get("count", 1)
                    issues.append(create_mock_issue(
                        category="quality",
                        severity="HIGH",
                        title=f"Images Missing Alt Text",
                        description=f"{count} image(s) are missing alt text attributes.",
                        impact="Missing alt text makes your content inaccessible to screen reader users.",
                        fix_steps=[
                            "Add descriptive alt text to all meaningful images",
                            "Use empty alt='' for decorative images",
                            "Ensure alt text conveys the image's purpose and content"
                        ],
                        estimated_time="10-20 minutes"
                    ))

                elif issue_type == "accessibility" and "labels" in issue["message"]:
                    issues.append(create_mock_issue(
                        category="quality",
                        severity="HIGH",
                        title="Form Elements Missing Labels",
                        description="Form inputs are found without proper label associations.",
                        impact="Unlabeled forms are inaccessible and confusing for screen reader users.",
                        fix_steps=[
                            "Add <label> elements for all form inputs",
                            "Use for/id attributes to associate labels with inputs",
                            "Consider using aria-label or aria-labelledby when appropriate"
                        ],
                        estimated_time="15-30 minutes"
                    ))

                elif issue_type == "deprecated":
                    count = issue.get("count", 1)
                    issues.append(create_mock_issue(
                        category="quality",
                        severity="MEDIUM",
                        title=f"Deprecated HTML Elements Found",
                        description=f"{count} deprecated HTML element(s) are being used.",
                        impact="Deprecated elements may not work in modern browsers and indicate outdated code.",
                        fix_steps=[
                            "Replace <font> tags with CSS font styling",
                            "Replace <center> with CSS text-align: center",
                            "Remove <marquee> and <blink> elements entirely",
                            "Use modern HTML5 elements and CSS for styling"
                        ],
                        estimated_time="20-40 minutes"
                    ))

            # Check console errors
            if console_errors:
                issues.append(create_mock_issue(
                    category="quality",
                    severity="HIGH",
                    title="JavaScript Console Errors",
                    description=f"Found {len(console_errors)} JavaScript console error(s) that may affect functionality.",
                    impact="Console errors can break website functionality and create poor user experience.",
                    fix_steps=[
                        "Fix undefined variables and function calls",
                        "Handle network errors and API failures gracefully",
                        "Add proper error handling with try-catch blocks",
                        "Test your JavaScript in multiple browsers"
                    ],
                    estimated_time="30-60 minutes"
                ))

        except Exception as e:
            logger.error(f"Error analyzing quality data: {str(e)}")

        return issues

    def _create_category_result(self, issues: List[Issue], category: str) -> CategoryResult:
        """Create a category result from a list of issues"""
        if not issues:
            return CategoryResult(score=100, issues_count=0, issues=[])

        # Calculate score based on issue severity
        total_score = 100
        for issue in issues:
            if issue.severity == "HIGH":
                total_score -= 25
            elif issue.severity == "MEDIUM":
                total_score -= 15
            elif issue.severity == "LOW":
                total_score -= 5

        # Ensure score doesn't go below 0
        score = max(0, total_score)

        return CategoryResult(
            score=score,
            issues_count=len(issues),
            issues=issues
        )

    def _extract_performance_metrics(self, performance_data: Dict[str, Any]) -> Optional[PerformanceMetrics]:
        """Extract performance metrics from scan data"""
        try:
            timing = performance_data.get("timing", {})
            resources = performance_data.get("resources", {})
            web_vitals = performance_data.get("web_vitals", {})

            return PerformanceMetrics(
                page_load_time=timing.get("loadComplete", 0) / 1000,
                total_size_kb=resources.get("totalSize", 0),
                requests_count=resources.get("totalRequests", 0),
                lcp=web_vitals.get("lcp", 0) / 1000 if web_vitals.get("lcp") else None,
                fid=None,  # Requires user interaction to measure
                cls=None,  # More complex to measure
                ttfb=timing.get("firstByte", 0) / 1000
            )

        except Exception as e:
            logger.error(f"Error extracting performance metrics: {str(e)}")
            return None

    def _init_security_rules(self) -> Dict[str, Any]:
        """Initialize security analysis rules"""
        return {
            "required_headers": [
                "content-security-policy",
                "x-frame-options",
                "strict-transport-security",
                "x-content-type-options",
                "referrer-policy"
            ]
        }

    def _init_performance_rules(self) -> Dict[str, Any]:
        """Initialize performance analysis rules"""
        return {
            "max_load_time": 3.0,  # seconds
            "max_page_size": 2000,  # KB
            "max_requests": 100,
            "max_lcp": 2.5  # seconds
        }

    def _init_quality_rules(self) -> Dict[str, Any]:
        """Initialize quality analysis rules"""
        return {
            "require_doctype": True,
            "require_headings": True,
            "require_alt_text": True,
            "require_form_labels": True
        }