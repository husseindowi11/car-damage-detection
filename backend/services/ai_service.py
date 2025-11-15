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
    DAMAGE_ANALYSIS_PROMPT = """You are an expert automotive damage assessor. Compare BEFORE and AFTER vehicle images to detect NEW damage only.

BEFORE images: Vehicle at pickup
AFTER images: Vehicle at return

Your task:
1. Examine BEFORE images to understand initial condition
2. Examine AFTER images for potential damage
3. Compare both sets - only report damage that is NEW (not in BEFORE images)

IMPORTANT - BE ACCURATE, NOT THOROUGH:
• Only report CLEAR, OBVIOUS, PHYSICAL damage
• Damage must be visible in multiple angles to confirm it's real
• When in doubt, DO NOT report it

DO NOT report:
• Dirt, dust, or mud
• Lighting differences or shadows
• Reflections or glare
• Water spots or rain drops
• Existing damage already in BEFORE images
• Minor imperfections that were already there
• Unclear marks that might be dirt

Only report these types of CLEAR damage:
• Dents (visible deformation of metal/plastic)
• Deep scratches (paint removed, exposing primer or metal)
• Cracks (in bumpers, lights, glass, panels)
• Broken parts (mirrors, lights, trim pieces)
• Major paint damage (large chips, scrapes)

For each confirmed NEW damage:
• car_part: specific part name
• damage_type: dent, scratch, crack, broken, paint_damage
• severity: minor, moderate, major
• recommended_action: repair, repaint, replace
• estimated_cost_usd: realistic cost ($60-120/hr labor, $200-450/panel paint)
• description: brief description
• image_index: which AFTER image (1, 2, 3, etc.)
• bounding_box: CRITICAL - Follow these steps exactly:
  1. Locate the EXACT position of the damage in the image
  2. Calculate coordinates as PERCENTAGES (0.0 to 1.0):
     - x_min_pct: LEFT edge of damage ÷ image width (0.0 = far left, 1.0 = far right)
     - y_min_pct: TOP edge of damage ÷ image height (0.0 = top, 1.0 = bottom)
     - x_max_pct: RIGHT edge of damage ÷ image width (0.0 = far left, 1.0 = far right)
     - y_max_pct: BOTTOM edge of damage ÷ image height (0.0 = top, 1.0 = bottom)
  3. Add 10-15% padding around the damage to ensure it's fully visible
  4. Verify coordinates make sense: x_max > x_min, y_max > y_min
  
  Example: Damage on rear bumper at bottom-right of image
  - Damage is at 70-85% horizontally, 75-90% vertically
  - Result: {"x_min_pct": 0.70, "y_min_pct": 0.75, "x_max_pct": 0.85, "y_max_pct": 0.90}

Output format (JSON only, no markdown):
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

If no new damage: return {"new_damage": [], "total_estimated_cost_usd": 0, "summary": "No new damage detected."}

CRITICAL RULES:
1. Bounding box coordinates MUST be accurate - they will be drawn on the image
2. Double-check each coordinate value before finalizing
3. Ensure the box fully contains the damage with small padding
4. All percentages must be between 0.0 and 1.0
5. x_max must be greater than x_min, y_max must be greater than y_min

Images provided: BEFORE images first, then AFTER images."""
    
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
    

