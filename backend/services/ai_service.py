"""
AI Service for vehicle damage detection using Google Gemini Vision
"""
import os
import json
import base64
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import google.generativeai as genai
from PIL import Image

logger = logging.getLogger(__name__)


class AIService:
    """Service for AI-powered damage detection using Google Gemini Vision"""
    
    # The exact prompt as specified in the requirements
    DAMAGE_ANALYSIS_PROMPT = """You are an expert automotive damage assessor for a car rental company. You specialize in before/after vehicle comparison, collision damage detection, and generating real-world repair estimates using industry-standard pricing (CCC One, Mitchell, Audatex).

You will receive TWO images:

BEFORE image – vehicle at pickup

AFTER image – vehicle at return

Your tasks:

Compare both images carefully.

Detect ONLY the NEW damages visible in the AFTER image.

Ignore all pre-existing damage visible in the BEFORE image.

For each new damage, identify:

the specific car part (e.g., rear bumper, front bumper, right fender, trunk lid, quarter panel, tail light, door)

the type of damage (dent, scratch, crack, broken light, paint damage, deformation, misalignment)

a short human-readable description

severity (minor, moderate, major)

recommended action (repair, repaint, replace)

a realistic repair cost estimate in USD using:
• labor: $60–$120/hr
• paint/materials: $200–$450 per panel
• OEM/aftermarket part pricing
• damage complexity

Output ONLY a JSON object in the following structure:

{
  "new_damage": [
    {
      "car_part": "",
      "damage_type": "",
      "severity": "",
      "recommended_action": "",
      "estimated_cost_usd": 0,
      "description": ""
    }
  ],
  "total_estimated_cost_usd": 0,
  "summary": ""
}

Rules:

Do NOT include bounding box coordinates.

Do NOT include explanations outside JSON.

If no new damage exists, return:

{
  "new_damage": [],
  "total_estimated_cost_usd": 0,
  "summary": "No new damage detected."
}

Wait for the two input images. The FIRST is BEFORE. The SECOND is AFTER."""
    
    def __init__(self):
        """Initialize AI service with Google Gemini API"""
        self.api_key = os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not found in environment variables")
            raise ValueError("GEMINI_API_KEY is required")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Initialize the model (Gemini 1.5 Pro supports vision)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        
        logger.info("AI Service initialized successfully")
    
    async def analyze_damage(
        self, 
        before_image_path: str, 
        after_image_path: str
    ) -> Dict[str, Any]:
        """
        Analyze vehicle images to detect new damages.
        
        Args:
            before_image_path: Path to BEFORE image
            after_image_path: Path to AFTER image
        
        Returns:
            Dictionary containing damage report and annotated image
        """
        try:
            logger.info("Starting damage analysis")
            
            # Load images
            before_image = Image.open(before_image_path)
            after_image = Image.open(after_image_path)
            
            # Prepare content for Gemini (prompt + images)
            content = [
                self.DAMAGE_ANALYSIS_PROMPT,
                before_image,
                after_image
            ]
            
            # Generate response
            logger.info("Sending request to Gemini API")
            response = self.model.generate_content(content)
            
            # Parse JSON response
            report = self._parse_gemini_response(response.text)
            
            # Generate annotated image (base64 encoded)
            annotated_image_base64 = self._create_annotated_image(
                after_image_path, 
                report
            )
            
            return {
                "report": report,
                "annotated_image_base64": annotated_image_base64
            }
            
        except Exception as e:
            logger.error(f"Error in damage analysis: {str(e)}")
            raise Exception(f"AI analysis failed: {str(e)}")
    
    def _parse_gemini_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse Gemini's text response into JSON.
        
        Args:
            response_text: Raw text response from Gemini
        
        Returns:
            Parsed JSON report
        """
        try:
            # Clean response text (remove markdown code blocks if present)
            cleaned_text = response_text.strip()
            
            # Remove markdown code block markers
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]
            
            cleaned_text = cleaned_text.strip()
            
            # Parse JSON
            report = json.loads(cleaned_text)
            
            # Validate structure
            if "new_damage" not in report:
                raise ValueError("Invalid report structure: missing 'new_damage'")
            
            logger.info(f"Parsed report: {len(report.get('new_damage', []))} damages found")
            
            return report
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            logger.error(f"Response text: {response_text}")
            
            # Return fallback structure
            return {
                "new_damage": [],
                "total_estimated_cost_usd": 0,
                "summary": "Error parsing AI response",
                "error": str(e)
            }
    
    def _create_annotated_image(
        self, 
        image_path: str, 
        report: Dict[str, Any]
    ) -> Optional[str]:
        """
        Create annotated image highlighting damages.
        
        Args:
            image_path: Path to the AFTER image
            report: Damage report from AI
        
        Returns:
            Base64 encoded annotated image
        """
        try:
            # For MVP, we'll return the original image base64
            # In production, you could draw bounding boxes/annotations using PIL
            with open(image_path, "rb") as image_file:
                image_bytes = image_file.read()
                image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            
            return image_base64
            
        except Exception as e:
            logger.error(f"Error creating annotated image: {str(e)}")
            return None

