"""
Pydantic models for API request/response schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class DamageItem(BaseModel):
    """Individual damage item detected in vehicle"""
    car_part: str = Field(..., description="Specific car part affected (e.g., rear bumper, front bumper, right fender)")
    damage_type: str = Field(..., description="Type of damage (dent, scratch, crack, broken light, paint damage, deformation, misalignment)")
    severity: str = Field(..., description="Severity level: minor, moderate, or major")
    recommended_action: str = Field(..., description="Recommended action: repair, repaint, or replace")
    estimated_cost_usd: float = Field(..., description="Estimated repair cost in USD", ge=0)
    description: str = Field(..., description="Short human-readable description of the damage")
    
    class Config:
        json_schema_extra = {
            "example": {
                "car_part": "rear bumper",
                "damage_type": "dent",
                "severity": "moderate",
                "recommended_action": "repair",
                "estimated_cost_usd": 350.0,
                "description": "Dent on rear bumper, approximately 3 inches in diameter"
            }
        }


class DamageReport(BaseModel):
    """Damage report structure from AI analysis"""
    new_damage: List[DamageItem] = Field(..., description="List of new damages detected")
    total_estimated_cost_usd: float = Field(..., description="Total estimated repair cost in USD", ge=0)
    summary: str = Field(..., description="Summary of the damage assessment")
    
    class Config:
        json_schema_extra = {
            "example": {
                "new_damage": [
                    {
                        "car_part": "rear bumper",
                        "damage_type": "dent",
                        "severity": "moderate",
                        "recommended_action": "repair",
                        "estimated_cost_usd": 350.0,
                        "description": "Dent on rear bumper, approximately 3 inches in diameter"
                    }
                ],
                "total_estimated_cost_usd": 350.0,
                "summary": "1 new damage detected on rear bumper"
            }
        }


class SavedImages(BaseModel):
    """Paths to saved images"""
    before: List[str] = Field(..., description="List of paths to saved BEFORE images (multiple angles)")
    after: List[str] = Field(..., description="List of paths to saved AFTER images (multiple angles)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "before": [
                    "uploads/2024-01-15/abc123/before_1.jpg",
                    "uploads/2024-01-15/abc123/before_2.jpg"
                ],
                "after": [
                    "uploads/2024-01-15/abc123/after_1.jpg",
                    "uploads/2024-01-15/abc123/after_2.jpg"
                ]
            }
        }


class InspectionResponse(BaseModel):
    """Response from /inspect endpoint"""
    success: bool = Field(..., description="Whether the inspection was successful")
    inspection_id: str = Field(..., description="Unique identifier for this inspection")
    car_name: str = Field(..., description="Car name")
    car_model: str = Field(..., description="Car model")
    car_year: int = Field(..., description="Car year")
    report: DamageReport = Field(..., description="Damage analysis report")
    saved_images: SavedImages = Field(..., description="Paths to permanently saved images (multiple angles)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "inspection_id": "550e8400-e29b-41d4-a716-446655440000",
                "car_name": "Toyota Corolla",
                "car_model": "SE",
                "car_year": 2020,
                "report": {
                    "new_damage": [
                        {
                            "car_part": "rear bumper",
                            "damage_type": "dent",
                            "severity": "moderate",
                            "recommended_action": "repair",
                            "estimated_cost_usd": 350.0,
                            "description": "Dent on rear bumper, approximately 3 inches in diameter"
                        }
                    ],
                    "total_estimated_cost_usd": 350.0,
                    "summary": "1 new damage detected on rear bumper"
                },
                "saved_images": {
                    "before": [
                        "uploads/2024-01-15/550e8400-e29b-41d4-a716-446655440000/before_1.jpg",
                        "uploads/2024-01-15/550e8400-e29b-41d4-a716-446655440000/before_2.jpg"
                    ],
                    "after": [
                        "uploads/2024-01-15/550e8400-e29b-41d4-a716-446655440000/after_1.jpg",
                        "uploads/2024-01-15/550e8400-e29b-41d4-a716-446655440000/after_2.jpg"
                    ]
                }
            }
        }


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    ai_service: str = Field(..., description="AI service provider")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "service": "vehicle-damage-detection",
                "ai_service": "google-gemini-vision"
            }
        }


class RootResponse(BaseModel):
    """Root endpoint response"""
    message: str = Field(..., description="API message")
    version: str = Field(..., description="API version")
    status: str = Field(..., description="API status")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Vehicle Damage Detection API",
                "version": "1.0.0",
                "status": "running"
            }
        }


class ErrorResponse(BaseModel):
    """Error response structure - standardized format"""
    status: bool = Field(False, description="Always false for errors")
    message: str = Field(..., description="Error message describing what went wrong")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional error details (optional)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": False,
                "message": "Validation error: Invalid file type. Allowed types: .jpg, .jpeg, .png, .webp",
                "data": {
                    "error_type": "ValidationError",
                    "field": "file_type"
                }
            }
        }
