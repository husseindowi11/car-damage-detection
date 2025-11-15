"""
AI Service for vehicle damage detection using Google Gemini Vision
"""
import os
import json
import logging
from typing import Dict, Any, List
from pathlib import Path
import google.generativeai as genai
from PIL import Image

logger = logging.getLogger(__name__)


class AIService:
    """Service for AI-powered damage detection using Google Gemini Vision"""
    
    # The exact prompt as specified in the requirements (updated for multiple angles)
    DAMAGE_ANALYSIS_PROMPT = """You are an expert automotive damage assessor for a car rental company. You specialize in before/after vehicle comparison, collision damage detection, and generating real-world repair estimates using industry-standard pricing (CCC One, Mitchell, Audatex).

You will receive MULTIPLE images showing the vehicle from different angles:

BEFORE images – vehicle at pickup (from multiple angles: front, rear, left side, right side, interior, etc.)

AFTER images – vehicle at return (from the same angles)

Your tasks:

1. Carefully examine ALL BEFORE images to understand the vehicle's initial condition.

2. Carefully examine ALL AFTER images to identify ANY visible damage.

3. Compare BEFORE vs AFTER to determine which damages are NEW (not present in BEFORE images).

4. Report ALL new damages found in AFTER images that were NOT present in BEFORE images.

5. Be thorough - examine each car part carefully: bumpers, fenders, doors, hood, trunk, lights, mirrors, wheels, windows, panels.

6. Look for all types of damage: dents, scratches, cracks, deformation, paint damage, broken parts, misalignment.

7. Cross-reference multiple angles to confirm each damage and select the clearest view for bounding boxes.

For each new damage, identify:

the specific car part (e.g., rear bumper, front bumper, right fender, trunk lid, quarter panel, tail light, door)

the type of damage (dent, scratch, crack, broken light, paint damage, deformation, misalignment)

a short human-readable description

severity (minor, moderate, major)

recommended action (repair, repaint, replace)

which AFTER image index (1-based) shows this damage most clearly

precise bounding box coordinates for the damage location in that AFTER image, as percentages (0.0 to 1.0):
  • x_min_pct: left edge (0.0 = far left, 1.0 = far right)
  • y_min_pct: top edge (0.0 = top, 1.0 = bottom)
  • x_max_pct: right edge (0.0 = far left, 1.0 = far right)
  • y_max_pct: bottom edge (0.0 = top, 1.0 = bottom)

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
      "description": "",
      "image_index": 1,
      "bounding_box": {
        "x_min_pct": 0.0,
        "y_min_pct": 0.0,
        "x_max_pct": 0.0,
        "y_max_pct": 0.0
      }
    }
  ],
  "total_estimated_cost_usd": 0,
  "summary": ""
}

Rules:

BE THOROUGH - Report ALL new damages found, even minor ones like small scratches or dents.

ALWAYS include precise bounding box coordinates for each damage.

The bounding box must tightly fit around the visible damage area.

The image_index must refer to the AFTER image that shows this damage most clearly (1 = first AFTER image, 2 = second, etc.).

Do NOT miss any visible damage in the AFTER images - your job is to catch everything.

Output ONLY valid JSON - no explanations, no markdown formatting, just the raw JSON object.

If no new damage exists, return:

{
  "new_damage": [],
  "total_estimated_cost_usd": 0,
  "summary": "No new damage detected."
}

The images will be provided in order: all BEFORE images first, then all AFTER images."""
    
    def __init__(self):
        """Initialize AI service with Google Gemini API"""
        self.api_key = os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not found in environment variables")
            raise ValueError("GEMINI_API_KEY is required")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Initialize the model - using gemini-2.5-flash (stable, multimodal, 1M tokens)
        # This model supports multimodal inputs (text + images)
        model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.model = genai.GenerativeModel(model_name)
        logger.info(f"AI Service initialized with model: {model_name}")
    
    async def analyze_damage(
        self, 
        before_image_paths: list[str], 
        after_image_paths: list[str]
    ) -> Dict[str, Any]:
        """
        Analyze vehicle images from multiple angles to detect new damages.
        
        Args:
            before_image_paths: List of paths to BEFORE images (multiple angles)
            after_image_paths: List of paths to AFTER images (multiple angles)
        
        Returns:
            Dictionary containing damage report
        """
        try:
            logger.info(f"Starting damage analysis with {len(before_image_paths)} BEFORE and {len(after_image_paths)} AFTER images")
            
            # Prepare content for Gemini (prompt + all images)
            content = [self.DAMAGE_ANALYSIS_PROMPT]
            
            # Add all BEFORE images
            for i, before_path in enumerate(before_image_paths, 1):
                before_image = Image.open(before_path)
                content.append(f"BEFORE Image {i}:")
                content.append(before_image)
            
            # Add all AFTER images
            for i, after_path in enumerate(after_image_paths, 1):
                after_image = Image.open(after_path)
                content.append(f"AFTER Image {i}:")
                content.append(after_image)
            
            # Generate response
            logger.info("Sending request to Gemini API with multiple images")
            response = self.model.generate_content(content)
            
            # Parse JSON response
            report = self._parse_gemini_response(response.text)
            
            logger.info(f"Analysis completed: {len(report.get('new_damage', []))} damages detected")
            
            return {
                "report": report
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
    

