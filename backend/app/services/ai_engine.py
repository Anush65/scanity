"""
AI Engine service for generating intelligent recommendations using Ollama
"""
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional
import httpx

from ..models.scan import Issue
from ..config import settings
from ..utils.helpers import create_mock_issue

logger = logging.getLogger(__name__)


class AIEngine:
    """Service for AI-powered issue analysis and recommendations"""

    def __init__(self):
        self.ollama_host = settings.ollama_host
        self.ollama_model = settings.ollama_model
        self.timeout = settings.ollama_timeout
        self.client = httpx.AsyncClient(timeout=self.timeout)

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.client.aclose()

    async def enhance_issues_with_ai(self, issues: List[Issue], url: str) -> List[Issue]:
        """
        Enhance existing issues with AI-generated explanations and recommendations

        Args:
            issues: List of detected issues
            url: The URL that was scanned

        Returns:
            List of enhanced issues
        """
        if not issues:
            return issues

        try:
            # Check if Ollama is available
            if not await self._is_ollama_available():
                logger.warning("Ollama not available, using fallback responses")
                return self._apply_fallback_enhancements(issues)

            # Group issues by category for batch processing
            enhanced_issues = []
            categories = {}

            for issue in issues:
                if issue.category not in categories:
                    categories[issue.category] = []
                categories[issue.category].append(issue)

            # Process each category
            for category, category_issues in categories.items():
                try:
                    enhanced_category_issues = await self._enhance_category_issues(
                        category_issues, category, url
                    )
                    enhanced_issues.extend(enhanced_category_issues)
                except Exception as e:
                    logger.error(f"Error enhancing {category} issues: {str(e)}")
                    enhanced_issues.extend(category_issues)

            return enhanced_issues

        except Exception as e:
            logger.error(f"Error enhancing issues with AI: {str(e)}")
            return self._apply_fallback_enhancements(issues)

    async def generate_website_summary(self, scan_results: Dict[str, Any], url: str) -> Dict[str, Any]:
        """
        Generate AI-powered summary of website health

        Args:
            scan_results: Complete scan results
            url: The URL that was scanned

        Returns:
            Dictionary containing summary and recommendations
        """
        try:
            if not await self._is_ollama_available():
                return self._generate_fallback_summary(scan_results, url)

            categories = scan_results.get("categories", {})
            health_score = scan_results.get("health_score", 0)

            # Prepare data for AI analysis
            analysis_data = {
                "url": url,
                "health_score": health_score,
                "security": categories.get("security", {}),
                "performance": categories.get("performance", {}),
                "quality": categories.get("quality", {})
            }

            prompt = self._build_summary_prompt(analysis_data)

            response = await self._call_ollama(prompt)

            if response:
                return self._parse_summary_response(response, health_score)
            else:
                return self._generate_fallback_summary(scan_results, url)

        except Exception as e:
            logger.error(f"Error generating website summary: {str(e)}")
            return self._generate_fallback_summary(scan_results, url)

    async def _is_ollama_available(self) -> bool:
        """Check if Ollama service is available"""
        try:
            response = await self.client.get(f"{self.ollama_host}/api/tags")
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"Ollama not available: {str(e)}")
            return False

    async def _call_ollama(self, prompt: str) -> Optional[str]:
        """Make a request to Ollama API"""
        try:
            payload = {
                "model": self.ollama_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,  # Lower temperature for more consistent responses
                    "max_tokens": 1000
                }
            }

            response = await self.client.post(
                f"{self.ollama_host}/api/generate",
                json=payload
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error calling Ollama: {str(e)}")
            return None

    async def _enhance_category_issues(self, issues: List[Issue], category: str, url: str) -> List[Issue]:
        """Enhance issues within a specific category"""
        enhanced_issues = []

        # Process issues in smaller batches to avoid overwhelming the AI
        batch_size = 3
        for i in range(0, len(issues), batch_size):
            batch = issues[i:i + batch_size]

            try:
                prompt = self._build_issue_enhancement_prompt(batch, category, url)
                response = await self._call_ollama(prompt)

                if response:
                    enhanced_batch = self._parse_issue_enhancement_response(response, batch)
                    enhanced_issues.extend(enhanced_batch)
                else:
                    # Fallback to original issues if AI fails
                    enhanced_issues.extend(batch)

            except Exception as e:
                logger.error(f"Error enhancing issue batch: {str(e)}")
                enhanced_issues.extend(batch)

        return enhanced_issues

    def _build_issue_enhancement_prompt(self, issues: List[Issue], category: str, url: str) -> str:
        """Build prompt for enhancing issues"""
        issues_data = []
        for issue in issues:
            issues_data.append({
                "title": issue.title,
                "current_description": issue.description,
                "severity": issue.severity
            })

        prompt = f"""
You are a website security and performance expert analyzing scan results for beginners.

Website URL: {url}
Issue Category: {category}

Please enhance the following issue descriptions to be more beginner-friendly and provide actionable fix steps:

Issues to enhance:
{json.dumps(issues_data, indent=2)}

For each issue, provide a JSON response with this exact structure:
{{
    "enhancements": [
        {{
            "title": "same_title_as_input",
            "beginner_description": "Simple explanation of what the problem means",
            "impact": "Why this matters for the website in simple terms",
            "fix_steps": ["Step 1", "Step 2", "Step 3"],
            "estimated_time": "time estimate in minutes/hours",
            "code_example": "Optional code snippet for fix"
        }}
    ]
}}

Focus on:
- Clear, simple language that beginners can understand
- Step-by-step instructions that are easy to follow
- Practical solutions that developers can implement
- Realistic time estimates for implementation

Respond only with valid JSON.
"""
        return prompt

    def _parse_issue_enhancement_response(self, response: str, original_issues: List[Issue]) -> List[Issue]:
        """Parse AI response for issue enhancement"""
        try:
            # Try to extract JSON from the response
            start_idx = response.find("{")
            end_idx = response.rfind("}") + 1

            if start_idx == -1 or end_idx == 0:
                return original_issues

            json_str = response[start_idx:end_idx]
            data = json.loads(json_str)

            enhancements = data.get("enhancements", [])
            enhanced_issues = []

            for i, enhancement in enumerate(enhancements):
                if i < len(original_issues):
                    original_issue = original_issues[i]

                    enhanced_issue = Issue(
                        id=original_issue.id,
                        category=original_issue.category,
                        severity=original_issue.severity,
                        title=enhancement.get("title", original_issue.title),
                        description=enhancement.get("beginner_description", original_issue.description),
                        impact=enhancement.get("impact", "This issue affects your website's performance and security."),
                        fix_steps=enhancement.get("fix_steps", ["Contact a developer for assistance"]),
                        estimated_time=enhancement.get("estimated_time", "30 minutes"),
                        code_example=enhancement.get("code_example"),
                        affected_resources=original_issue.affected_resources
                    )
                    enhanced_issues.append(enhanced_issue)

            # Add any remaining original issues
            if len(enhancements) < len(original_issues):
                enhanced_issues.extend(original_issues[len(enhancements):])

            return enhanced_issues

        except Exception as e:
            logger.error(f"Error parsing issue enhancement response: {str(e)}")
            return original_issues

    def _build_summary_prompt(self, analysis_data: Dict[str, Any]) -> str:
        """Build prompt for website summary generation"""
        prompt = f"""
You are a website security and performance expert. Analyze the following scan results and provide a comprehensive summary.

Website: {analysis_data['url']}
Overall Health Score: {analysis_data['health_score']}/100

Security Analysis:
- Score: {analysis_data['security'].get('score', 0)}/100
- Issues Found: {analysis_data['security'].get('issues_count', 0)}

Performance Analysis:
- Score: {analysis_data['performance'].get('score', 0)}/100
- Issues Found: {analysis_data['performance'].get('issues_count', 0)}

Code Quality Analysis:
- Score: {analysis_data['quality'].get('score', 0)}/100
- Issues Found: {analysis_data['quality'].get('issues_count', 0)}

Please provide a JSON response with this structure:
{{
    "overall_status": "Excellent/Good/Fair/Poor",
    "summary": "2-3 sentence summary of website health",
    "key_strengths": ["strength 1", "strength 2"],
    "critical_issues": ["most important issue 1", "most important issue 2"],
    "recommendations": [
        {{
            "priority": "High/Medium/Low",
            "action": "Recommended action",
            "reason": "Why this action is important"
        }}
    ],
    "next_steps": ["immediate next step 1", "immediate next step 2"]
}}

Focus on actionable insights that help improve the website.
"""
        return prompt

    def _parse_summary_response(self, response: str, health_score: int) -> Dict[str, Any]:
        """Parse AI response for website summary"""
        try:
            # Try to extract JSON from the response
            start_idx = response.find("{")
            end_idx = response.rfind("}") + 1

            if start_idx == -1 or end_idx == 0:
                return self._generate_fallback_summary({}, "")

            json_str = response[start_idx:end_idx]
            data = json.loads(json_str)

            return {
                "ai_generated": True,
                "health_score": health_score,
                "overall_status": data.get("overall_status", "Fair"),
                "summary": data.get("summary", f"Website analysis completed with a health score of {health_score}/100."),
                "key_strengths": data.get("key_strengths", []),
                "critical_issues": data.get("critical_issues", []),
                "recommendations": data.get("recommendations", []),
                "next_steps": data.get("next_steps", [])
            }

        except Exception as e:
            logger.error(f"Error parsing summary response: {str(e)}")
            return self._generate_fallback_summary({}, "")

    def _apply_fallback_enhancements(self, issues: List[Issue]) -> List[Issue]:
        """Apply fallback enhancements when AI is not available"""
        enhanced_issues = []

        for issue in issues:
            # Use predefined templates based on issue type
            enhanced_issue = self._get_fallback_issue(issue)
            enhanced_issues.append(enhanced_issue)

        return enhanced_issues

    def _get_fallback_issue(self, original_issue: Issue) -> Issue:
        """Get fallback issue with enhanced descriptions"""
        fallback_templates = {
            "security": {
                "description": "This security issue could expose your website to attacks and compromise user data.",
                "impact": "Security vulnerabilities can lead to data breaches, loss of user trust, and legal consequences.",
                "fix_steps": [
                    "Review the specific security recommendation",
                    "Implement the suggested security measures",
                    "Test the fix to ensure it works correctly",
                    "Consider consulting with a security expert"
                ],
                "estimated_time": "30-60 minutes"
            },
            "performance": {
                "description": "This performance issue slows down your website and negatively impacts user experience.",
                "impact": "Slow websites have higher bounce rates, lower conversion rates, and poor search engine rankings.",
                "fix_steps": [
                    "Identify the specific performance bottleneck",
                    "Implement the optimization suggested",
                    "Test the improvement using performance tools",
                    "Monitor performance after deployment"
                ],
                "estimated_time": "15-45 minutes"
            },
            "quality": {
                "description": "This code quality issue affects maintainability and user experience.",
                "impact": "Poor code quality can lead to bugs, accessibility issues, and difficulty in future development.",
                "fix_steps": [
                    "Review the code quality recommendation",
                    "Update your code to follow best practices",
                    "Test the changes thoroughly",
                    "Document any changes made"
                ],
                "estimated_time": "20-40 minutes"
            }
        }

        template = fallback_templates.get(original_issue.category, fallback_templates["quality"])

        return Issue(
            id=original_issue.id,
            category=original_issue.category,
            severity=original_issue.severity,
            title=original_issue.title,
            description=original_issue.description or template["description"],
            impact=original_issue.impact or template["impact"],
            fix_steps=original_issue.fix_steps or template["fix_steps"],
            estimated_time=original_issue.estimated_time or template["estimated_time"],
            code_example=original_issue.code_example,
            affected_resources=original_issue.affected_resources
        )

    def _generate_fallback_summary(self, scan_results: Dict[str, Any], url: str) -> Dict[str, Any]:
        """Generate fallback summary when AI is not available"""
        health_score = scan_results.get("health_score", 0)

        if health_score >= 90:
            status = "Excellent"
            summary = "Your website is in excellent condition with minimal issues found."
        elif health_score >= 70:
            status = "Good"
            summary = "Your website is in good condition but has some areas that could be improved."
        elif health_score >= 50:
            status = "Fair"
            summary = "Your website has several issues that should be addressed to improve performance and security."
        else:
            status = "Poor"
            summary = "Your website has significant issues that require immediate attention."

        return {
            "ai_generated": False,
            "health_score": health_score,
            "overall_status": status,
            "summary": summary,
            "key_strengths": [
                "Regular scanning helps maintain website health",
                "Identifying issues is the first step to improvement"
            ],
            "critical_issues": [
                "Address high-severity security issues first",
                "Focus on performance optimizations for better user experience"
            ],
            "recommendations": [
                {
                    "priority": "High",
                    "action": "Address all HIGH severity issues",
                    "reason": "High severity issues pose the greatest risk to your website"
                },
                {
                    "priority": "Medium",
                    "action": "Implement performance optimizations",
                    "reason": "Performance improvements enhance user experience"
                },
                {
                    "priority": "Low",
                    "action": "Fix code quality issues",
                    "reason": "Code quality improvements support long-term maintainability"
                }
            ],
            "next_steps": [
                "Review detailed issue descriptions and fix steps",
                "Implement changes starting with high-priority issues",
                "Re-scan your website after making changes"
            ]
        }