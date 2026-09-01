"""
Gemini AI Integration Module for CivicTrack
Provides AI-powered analysis for incident severity, recommendations, and insights
"""

import os
import json
from typing import Dict, List, Optional

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("WARNING: google-generativeai not installed. AI features will be limited.")


class GeminiAnalyzer:
    """
    AI-powered incident analyzer using Google's Gemini API
    Provides intelligent severity assessment, automated recommendations, and insights
    """
    
    def __init__(self):
        self.api_key = os.environ.get('GEMINI_API_KEY')
        self.available = GEMINI_AVAILABLE and self.api_key is not None
        
        if self.available:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None
    
    def analyze_incident_severity(self, 
                                  category: str, 
                                  description: str, 
                                  location: Optional[str] = None) -> Dict[str, any]:
        """
        Analyzes incident and provides AI-powered severity assessment
        
        Args:
            category: Issue category (e.g., 'Power Grid', 'Water Supply')
            description: Detailed incident description
            location: Location/address of incident
        
        Returns:
            Dictionary with severity level, confidence score, and reasoning
        """
        
        if not self.available:
            return self._fallback_severity_assessment(category, description)
        
        try:
            prompt = f"""Analyze this municipal incident and provide severity assessment:

Category: {category}
Description: {description}
Location: {location or 'Not specified'}

Provide ONLY a JSON response with:
{{
    "severity": "Critical|High|Medium|Low",
    "confidence": 0.95,
    "reasoning": "Brief explanation",
    "risk_factors": ["factor1", "factor2"],
    "immediate_action": "Recommended action"
}}"""
            
            response = self.model.generate_content(prompt)
            
            # Extract JSON from response
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            result = json.loads(response_text.strip())
            return result
            
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return self._fallback_severity_assessment(category, description)
    
    def generate_resolution_guidance(self, 
                                     issue_id: int,
                                     category: str, 
                                     description: str,
                                     severity: str) -> Dict[str, any]:
        """
        Generates AI-powered resolution guidance for administrators
        
        Args:
            issue_id: Issue identifier
            category: Issue category
            description: Issue description
            severity: Current severity level
        
        Returns:
            Dictionary with recommendations and guidance
        """
        
        if not self.available:
            return {
                "recommendations": ["Contact relevant department"],
                "timeline": "Depends on severity",
                "resources": []
            }
        
        try:
            prompt = f"""As a municipal incident resolution expert, provide actionable guidance:

Issue #{issue_id}
Category: {category}
Severity: {severity}
Description: {description}

Provide ONLY a JSON response with:
{{
    "recommendations": ["action1", "action2", "action3"],
    "timeline_hours": 24,
    "required_departments": ["dept1", "dept2"],
    "escalation_criteria": "When to escalate further",
    "cost_estimate": "Estimated resolution cost (Low/Medium/High)"
}}"""
            
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean JSON extraction
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0]
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0]
            
            result = json.loads(response_text.strip())
            return result
            
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return {
                "recommendations": ["Assess on-site conditions", "Coordinate with relevant department"],
                "timeline_hours": 48,
                "required_departments": [category],
                "escalation_criteria": "If severity increases",
                "cost_estimate": "Medium"
            }
    
    def extract_insights_from_batch(self, issues: List[Dict]) -> Dict[str, any]:
        """
        Analyzes multiple incidents to provide city-wide insights
        
        Args:
            issues: List of issue dictionaries
        
        Returns:
            Dictionary with patterns, trends, and recommendations
        """
        
        if not self.available or len(issues) < 3:
            return {
                "patterns": [],
                "hotspots": [],
                "recommendations": []
            }
        
        try:
            issues_summary = "\n".join([
                f"- {i['category']}: {i['description'][:100]} (Severity: {i['severity']})"
                for i in issues[:10]
            ])
            
            prompt = f"""Analyze these municipal incidents and provide insights:

{issues_summary}

Provide ONLY a JSON response with:
{{
    "patterns": ["pattern1", "pattern2"],
    "infrastructure_hotspots": ["location1", "location2"],
    "category_trends": {{"category": count}},
    "systemic_recommendations": ["recommendation1", "recommendation2"]
}}"""
            
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0]
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0]
            
            result = json.loads(response_text.strip())
            return result
            
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return {
                "patterns": ["Multiple incidents in same category"],
                "infrastructure_hotspots": ["Analysis pending"],
                "recommendations": ["Monitor trends", "Allocate resources"]
            }
    
    def _fallback_severity_assessment(self, category: str, description: str) -> Dict[str, any]:
        """
        Fallback assessment when Gemini API is unavailable
        Uses rule-based heuristics for severity
        """
        desc_lower = description.lower()
        
        critical_keywords = ['fire', 'explosion', 'collapse', 'electrocution', 
                            'flooding', 'hazardous', 'imminent danger', 'live wire']
        high_keywords = ['outage', 'leak', 'sewage', 'blocked', 'broken', 
                        'gas smell', 'traffic risk']
        
        if any(kw in desc_lower for kw in critical_keywords):
            severity = 'Critical'
            confidence = 0.85
        elif any(kw in desc_lower for kw in high_keywords) or category in ['Power Grid']:
            severity = 'High'
            confidence = 0.75
        elif category in ['Water Supply', 'Sanitation']:
            severity = 'Medium'
            confidence = 0.70
        else:
            severity = 'Low'
            confidence = 0.65
        
        return {
            "severity": severity,
            "confidence": confidence,
            "reasoning": "Rule-based assessment (Gemini API unavailable)",
            "risk_factors": ["Requires AI analysis"],
            "immediate_action": "Monitor and escalate if conditions worsen"
        }


# Global singleton instance
_analyzer_instance = None

def get_analyzer() -> GeminiAnalyzer:
    """Get or create the Gemini analyzer instance"""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = GeminiAnalyzer()
    return _analyzer_instance
