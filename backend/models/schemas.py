"""
Pydantic models for API request/response schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class BoundingBox(BaseModel):
    """Bounding box coordinates for damage location (as percentages 0.0-1.0)"""
    x_min_pct: float = Field(..., description="Left edge (0.0 = far left, 1.0 = far right)", ge=0.0, le=1.0)
    y_min_pct: float = Field(..., description="Top edge (0.0 = top, 1.0 = bottom)", ge=0.0, le=1.0)
    x_max_pct: float = Field(..., description="Right edge (0.0 = far left, 1.0 = far right)", ge=0.0, le=1.0)
    y_max_pct: float = Field(..., description="Bottom edge (0.0 = top, 1.0 = bottom)", ge=0.0, le=1.0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "x_min_pct": 0.15,
                "y_min_pct": 0.22,
                "x_max_pct": 0.41,
                "y_max_pct": 0.48
            }
        }


class DamageItem(BaseModel):
    """Individual damage item detected in vehicle"""
    car_part: str = Field(..., description="Specific car part affected (e.g., rear bumper, front bumper, right fender)")
    damage_type: str = Field(..., description="Type of damage (dent, scratch, crack, broken light, paint damage, deformation, misalignment)")
    severity: str = Field(..., description="Severity level: minor, moderate, or major")
    recommended_action: str = Field(..., description="Recommended action: repair, repaint, or replace")
    estimated_cost_usd: float = Field(..., description="Estimated repair cost in USD", ge=0)
    description: str = Field(..., description="Short human-readable description of the damage")
    image_index: int = Field(..., description="AFTER image index (1-based) that shows this damage most clearly", ge=1)
    bounding_box: BoundingBox = Field(..., description="Bounding box coordinates for damage location in the specified AFTER image")
    
    class Config:
        json_schema_extra = {
            "example": {
                "car_part": "rear bumper",
                "damage_type": "dent",
                "severity": "moderate",
                "recommended_action": "repair",
                "estimated_cost_usd": 350.0,
                "description": "Dent on rear bumper, approximately 3 inches in diameter",
                "image_index": 1,
                "bounding_box": {
                    "x_min_pct": 0.15,
                    "y_min_pct": 0.22,
                    "x_max_pct": 0.41,
                    "y_max_pct": 0.48
                }
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
    bounded: List[str] = Field(default=[], description="List of paths to AFTER images with bounding boxes drawn (only if damages detected)")
    
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
                ],
                "bounded": [
                    "uploads/2024-01-15/abc123/bounded_1.jpg",
                    "uploads/2024-01-15/abc123/bounded_2.jpg"
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
                    ],
                    "bounded": [
                        "uploads/2024-01-15/550e8400-e29b-41d4-a716-446655440000/bounded_1.jpg"
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


# Inspection Detail and List Schemas
class InspectionDetail(BaseModel):
    """Inspection detail schema for API responses"""
    id: str = Field(..., description="Unique inspection identifier")
    car_name: str = Field(..., description="Car name")
    car_model: str = Field(..., description="Car model")
    car_year: int = Field(..., description="Car manufacturing year")
    damage_report: DamageReport = Field(..., description="Full damage analysis report")
    total_damage_cost: float = Field(..., description="Total estimated damage cost in USD")
    before_images: List[str] = Field(..., description="List of BEFORE image paths")
    after_images: List[str] = Field(..., description="List of AFTER image paths")
    bounded_images: List[str] = Field(default=[], description="List of AFTER images with bounding boxes drawn (only if damages detected)")
    created_at: str = Field(..., description="Inspection creation timestamp")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "car_name": "Toyota Corolla",
                "car_model": "SE",
                "car_year": 2020,
                "damage_report": {
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
                "total_damage_cost": 350.0,
                "before_images": [
                    "uploads/2024-01-15/550e8400-e29b-41d4-a716-446655440000/before_1.jpg"
                ],
                "after_images": [
                    "uploads/2024-01-15/550e8400-e29b-41d4-a716-446655440000/after_1.jpg"
                ],
                "bounded_images": [
                    "uploads/2024-01-15/550e8400-e29b-41d4-a716-446655440000/bounded_1.jpg"
                ],
                "created_at": "2024-01-15T10:30:00"
            }
        }


class InspectionListItem(BaseModel):
    """Inspection list item schema (summary for list view)"""
    id: str = Field(..., description="Unique inspection identifier")
    car_name: str = Field(..., description="Car name")
    car_model: str = Field(..., description="Car model")
    car_year: int = Field(..., description="Car manufacturing year")
    total_damage_cost: float = Field(..., description="Total estimated damage cost in USD")
    created_at: str = Field(..., description="Inspection creation timestamp")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "car_name": "Toyota Corolla",
                "car_model": "SE",
                "car_year": 2020,
                "total_damage_cost": 350.0,
                "created_at": "2024-01-15T10:30:00"
            }
        }


class InspectionListData(BaseModel):
    """Data structure for inspection list response"""
    total: int = Field(..., description="Total number of inspections")
    inspections: List[InspectionListItem] = Field(..., description="List of inspections")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total": 2,
                "inspections": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "car_name": "Toyota Corolla",
                        "car_model": "SE",
                        "car_year": 2020,
                        "total_damage_cost": 350.0,
                        "created_at": "2024-01-15T10:30:00"
                    }
                ]
            }
        }


class InspectionListResponse(BaseModel):
    """Standardized response for inspection list"""
    status: bool = Field(..., description="Response status")
    message: str = Field(..., description="Response message")
    data: InspectionListData = Field(..., description="Inspection list data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": True,
                "message": "Inspections retrieved successfully",
                "data": {
                    "total": 2,
                    "inspections": []
                }
            }
        }


class InspectionDetailResponse(BaseModel):
    """Standardized response for inspection detail"""
    status: bool = Field(..., description="Response status")
    message: str = Field(..., description="Response message")
    data: InspectionDetail = Field(..., description="Inspection detail data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": True,
                "message": "Inspection retrieved successfully",
                "data": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "car_name": "Toyota Corolla",
                    "car_model": "SE",
                    "car_year": 2020,
                    "damage_report": {
                        "new_damage": [],
                        "total_estimated_cost_usd": 350.0,
                        "summary": "1 new damage detected"
                    },
                    "total_damage_cost": 350.0,
                    "before_images": [],
                    "after_images": [],
                    "created_at": "2024-01-15T10:30:00"
                }
            }
        }
