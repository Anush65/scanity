"""
Playwright-based website scanner service
"""
import asyncio
import time
import base64
from typing import Dict, List, Optional, Any
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
import logging

from ..models.scan import PerformanceMetrics
from ..config import settings
from ..utils.helpers import format_duration

logger = logging.getLogger(__name__)


class ScannerService:
    """Service for scanning websites using Playwright"""

    def __init__(self):
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None

    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.cleanup()

    async def initialize(self):
        """Initialize Playwright browser"""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-web-security",
                    "--disable-features=VizDisplayCompositor"
                ]
            )

            # Create browser context with custom settings
            self.context = await self.browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="ScanityBot/1.0 (Security and Performance Scanner)",
                ignore_https_errors=True
            )

            logger.info("Playwright browser initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Playwright: {str(e)}")
            raise

    async def cleanup(self):
        """Clean up Playwright resources"""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if hasattr(self, 'playwright'):
                await self.playwright.stop()
            logger.info("Playwright resources cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

    async def scan_website(self, url: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Perform comprehensive website scan

        Args:
            url: Website URL to scan
            options: Scan options

        Returns:
            Dictionary containing scan results
        """
        if not self.context:
            raise RuntimeError("Scanner not initialized. Call initialize() first.")

        options = options or {}
        include_screenshot = options.get("include_screenshot", True)
        mobile_view = options.get("mobile_view", False)

        # Set mobile viewport if requested
        if mobile_view:
            await self.context.set_viewport_size({"width": 375, "height": 667})

        start_time = time.time()
        scan_results = {}

        try:
            # Create new page
            page = await self.context.new_page()

            # Collect performance metrics
            performance_data = await self._collect_performance_metrics(page, url)

            # Collect security data
            security_data = await self._collect_security_data(page, url)

            # Collect code quality data
            quality_data = await self._collect_quality_data(page, url)

            # Take screenshot if requested
            if include_screenshot:
                screenshot_data = await self._take_screenshot(page)
                scan_results["screenshot"] = screenshot_data

            # Close page
            await page.close()

            # Combine all results
            scan_results.update({
                "url": url,
                "performance": performance_data,
                "security": security_data,
                "quality": quality_data,
                "scan_duration": time.time() - start_time
            })

            logger.info(f"Scan completed for {url} in {format_duration(scan_results['scan_duration'])}")
            return scan_results

        except Exception as e:
            logger.error(f"Error scanning {url}: {str(e)}")
            raise

    async def _collect_performance_metrics(self, page: Page, url: str) -> Dict[str, Any]:
        """Collect performance-related metrics"""
        try:
            # Navigate to page and wait for load
            response = await page.goto(url, wait_until="networkidle", timeout=30000)

            if not response:
                raise Exception("Failed to load page")

            # Get performance timing
            performance_timing = await page.evaluate("""
                () => {
                    const timing = performance.timing;
                    return {
                        domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart,
                        loadComplete: timing.loadEventEnd - timing.navigationStart,
                        firstByte: timing.responseStart - timing.navigationStart,
                        domInteractive: timing.domInteractive - timing.navigationStart
                    };
                }
            """)

            # Get Core Web Vitals
            web_vitals = await page.evaluate("""
                () => {
                    return new Promise((resolve) => {
                        // Simple LCP measurement
                        new PerformanceObserver((list) => {
                            const entries = list.getEntries();
                            const lastEntry = entries[entries.length - 1];
                            resolve({
                                lcp: lastEntry.startTime
                            });
                        }).observe({ entryTypes: ['largest-contentful-paint'] });

                        // Fallback timeout
                        setTimeout(() => resolve({ lcp: null }), 5000);
                    });
                }
            """)

            # Get resource information
            resources = await page.evaluate("""
                () => {
                    const resources = performance.getEntriesByType('resource');
                    const totalSize = resources.reduce((sum, resource) => {
                        return sum + (resource.transferSize || 0);
                    }, 0);

                    const resourceTypes = {};
                    resources.forEach(resource => {
                        const type = resource.initiatorType || 'other';
                        resourceTypes[type] = (resourceTypes[type] || 0) + 1;
                    });

                    return {
                        totalRequests: resources.length,
                        totalSize: Math.round(totalSize / 1024), // Convert to KB
                        resourceTypes: resourceTypes
                    };
                }
            """)

            return {
                "timing": performance_timing,
                "web_vitals": web_vitals,
                "resources": resources,
                "response_code": response.status,
                "response_headers": dict(response.headers)
            }

        except Exception as e:
            logger.error(f"Error collecting performance metrics: {str(e)}")
            return {"error": str(e)}

    async def _collect_security_data(self, page: Page, url: str) -> Dict[str, Any]:
        """Collect security-related data"""
        try:
            # Get response headers
            security_headers = await page.evaluate("""
                () => {
                    const headers = {};
                    // Security headers to check
                    const securityHeaderNames = [
                        'content-security-policy',
                        'x-frame-options',
                        'strict-transport-security',
                        'x-content-type-options',
                        'referrer-policy',
                        'permissions-policy'
                    ];

                    securityHeaderNames.forEach(name => {
                        const meta = document.querySelector(`meta[http-equiv="${name}"]`);
                        if (meta) {
                            headers[name] = meta.getAttribute('content');
                        }
                    });

                    return headers;
                }
            """)

            # Check for mixed content
            mixed_content = await page.evaluate("""
                () => {
                    const httpsResources = [];
                    const httpResources = [];

                    // Check images
                    document.querySelectorAll('img').forEach(img => {
                        const src = img.src;
                        if (src.startsWith('https://')) {
                            httpsResources.push(src);
                        } else if (src.startsWith('http://')) {
                            httpResources.push(src);
                        }
                    });

                    // Check scripts
                    document.querySelectorAll('script').forEach(script => {
                        const src = script.src;
                        if (src.startsWith('https://')) {
                            httpsResources.push(src);
                        } else if (src.startsWith('http://')) {
                            httpResources.push(src);
                        }
                    });

                    // Check stylesheets
                    document.querySelectorAll('link[rel="stylesheet"]').forEach(link => {
                        const href = link.href;
                        if (href.startsWith('https://')) {
                            httpsResources.push(href);
                        } else if (href.startsWith('http://')) {
                            httpResources.push(href);
                        }
                    });

                    return {
                        httpResources: httpResources.slice(0, 10), // Limit results
                        httpsResources: httpsResources.slice(0, 10),
                        hasMixedContent: httpResources.length > 0
                    };
                }
            """)

            # Check for exposed JavaScript variables
            exposed_vars = await page.evaluate("""
                () => {
                    const exposedVars = [];
                    const commonPatterns = [
                        /^api/i,
                        /key/i,
                        /secret/i,
                        /token/i,
                        /password/i,
                        /config/i
                    ];

                    for (let key in window) {
                        if (commonPatterns.some(pattern => pattern.test(key))) {
                            try {
                                const value = window[key];
                                if (typeof value === 'string' && value.length < 200) {
                                    exposedVars.push({ name: key, value: value });
                                }
                            } catch (e) {
                                // Skip variables that can't be accessed
                            }
                        }
                    }

                    return exposedVars.slice(0, 10); // Limit results
                }
            """)

            return {
                "security_headers": security_headers,
                "mixed_content": mixed_content,
                "exposed_variables": exposed_vars
            }

        except Exception as e:
            logger.error(f"Error collecting security data: {str(e)}")
            return {"error": str(e)}

    async def _collect_quality_data(self, page: Page, url: str) -> Dict[str, Any]:
        """Collect code quality and accessibility data"""
        try:
            # HTML structure analysis
            html_structure = await page.evaluate("""
                () => {
                    const issues = [];

                    // Check for DOCTYPE
                    if (!document.doctype) {
                        issues.push({
                            type: 'doctype',
                            message: 'Missing DOCTYPE declaration'
                        });
                    }

                    // Check heading structure
                    const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
                    if (headings.length === 0) {
                        issues.push({
                            type: 'headings',
                            message: 'No heading tags found'
                        });
                    }

                    // Check for images without alt text
                    const imagesWithoutAlt = document.querySelectorAll('img:not([alt])');
                    if (imagesWithoutAlt.length > 0) {
                        issues.push({
                            type: 'accessibility',
                            message: `${imagesWithoutAlt.length} images missing alt text`,
                            count: imagesWithoutAlt.length
                        });
                    }

                    // Check for forms without labels
                    const inputsWithoutLabels = document.querySelectorAll('input:not([aria-label]):not([placeholder])');
                    const inputsWithLabels = document.querySelectorAll('label[for]');

                    if (inputsWithoutLabels.length > inputsWithLabels.length) {
                        issues.push({
                            type: 'accessibility',
                            message: 'Form inputs found without proper labels'
                        });
                    }

                    // Check for deprecated elements
                    const deprecatedElements = document.querySelectorAll('font, center, marquee, blink');
                    if (deprecatedElements.length > 0) {
                        issues.push({
                            type: 'deprecated',
                            message: `${deprecatedElements.length} deprecated HTML elements found`,
                            count: deprecatedElements.length
                        });
                    }

                    return {
                        issues: issues,
                        totalHeadings: headings.length,
                        totalImages: document.querySelectorAll('img').length,
                        totalForms: document.querySelectorAll('form').length
                    };
                }
            """)

            # Console errors check
            console_errors = []
            page.on('console', lambda msg: None if msg.type != 'error' else console_errors.append(msg.text))

            # Wait a bit to collect console errors
            await asyncio.sleep(2)

            return {
                "html_structure": html_structure,
                "console_errors": console_errors[-10:] if console_errors else []  # Last 10 errors
            }

        except Exception as e:
            logger.error(f"Error collecting quality data: {str(e)}")
            return {"error": str(e)}

    async def _take_screenshot(self, page: Page) -> Optional[str]:
        """Take a screenshot of the page"""
        try:
            # Wait for page to be fully loaded
            await page.wait_for_load_state('networkidle', timeout=10000)

            # Take full page screenshot
            screenshot = await page.screenshot(
                full_page=True,
                type='png',
                quality=90
            )

            # Convert to base64 for storage/transmission
            screenshot_b64 = base64.b64encode(screenshot).decode('utf-8')
            return f"data:image/png;base64,{screenshot_b64}"

        except Exception as e:
            logger.error(f"Error taking screenshot: {str(e)}")
            return None