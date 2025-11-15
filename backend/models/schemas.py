"""
Pydantic models for API request/response schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


# Car-related enums
class CarModelEnum(str, Enum):
    """Predefined car models/trims"""
    SE = "SE"
    GLS = "GLS"
    SPORT = "Sport"
    LX = "LX"
    EX = "EX"
    TOURING = "Touring"
    BASE = "Base"
    PREMIUM = "Premium"
    LUXURY = "Luxury"


class CarStatusEnum(str, Enum):
    """Car status"""
    AVAILABLE = "available"
    RENTED = "rented"
    MAINTENANCE = "maintenance"
    RETIRED = "retired"


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


class InspectionRequest(BaseModel):
    """Request schema for /inspect endpoint"""
    booking_id: int = Field(..., description="Booking ID. Images must already be uploaded to the booking via the booking images API.", example=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "booking_id": 1
            }
        }


class InspectionResponse(BaseModel):
    """Response from /inspect endpoint"""
    success: bool = Field(..., description="Whether the inspection was successful")
    inspection_id: str = Field(..., description="Unique identifier for this inspection")
    report: DamageReport = Field(..., description="Damage analysis report")
    saved_images: SavedImages = Field(..., description="Paths to permanently saved images (multiple angles)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "inspection_id": "550e8400-e29b-41d4-a716-446655440000",
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


# Car CRUD schemas
class CarBase(BaseModel):
    """Base schema for Car with common fields"""
    name: str = Field(..., description="Full car name", example="Toyota Corolla")
    make: str = Field(..., description="Car manufacturer", example="Toyota")
    model: CarModelEnum = Field(..., description="Car model/trim", example="SE")
    year: int = Field(..., description="Manufacturing year", ge=1900, le=2100, example=2020)
    color: Optional[str] = Field(None, description="Car color", example="Silver")
    vin: Optional[str] = Field(None, description="Vehicle Identification Number", example="1HGBH41JXMN109186")
    license_plate: Optional[str] = Field(None, description="License plate number", example="ABC-1234")
    mileage: Optional[int] = Field(None, description="Current mileage in miles", ge=0, example=45000)
    status: CarStatusEnum = Field(CarStatusEnum.AVAILABLE, description="Current status of the car")


class CarCreate(CarBase):
    """Schema for creating a new car"""
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Toyota Corolla",
                "make": "Toyota",
                "model": "SE",
                "year": 2020,
                "color": "Silver",
                "vin": "1HGBH41JXMN109186",
                "license_plate": "ABC-1234",
                "mileage": 45000,
                "status": "available"
            }
        }


class CarUpdate(BaseModel):
    """
    Schema for updating a car - ALL fields are optional for partial updates.
    
    The car_id is provided in the URL path parameter, not in the request body.
    You can update any combination of fields:
    - Update just one field (e.g., only mileage)
    - Update multiple fields (e.g., mileage and status)
    - Update all fields (complete car information update)
    """
    name: Optional[str] = Field(None, description="Full car name (e.g., 'Toyota Corolla', 'Honda Civic')", example="Toyota Corolla")
    make: Optional[str] = Field(None, description="Car manufacturer (e.g., 'Toyota', 'Honda', 'Ford')", example="Toyota")
    model: Optional[CarModelEnum] = Field(None, description="Car model/trim. Options: SE, GLS, Sport, LX, EX, Touring, Base, Premium, Luxury", example="SE")
    year: Optional[int] = Field(None, description="Manufacturing year (1900-2100)", ge=1900, le=2100, example=2020)
    color: Optional[str] = Field(None, description="Car color (e.g., 'Silver', 'Black', 'White', 'Red')", example="Silver")
    vin: Optional[str] = Field(None, description="Vehicle Identification Number (must be unique if provided)", example="1HGBH41JXMN109186")
    license_plate: Optional[str] = Field(None, description="License plate number (must be unique if provided)", example="ABC-1234")
    mileage: Optional[int] = Field(None, description="Current mileage in miles (must be >= 0)", ge=0, example=45000)
    status: Optional[CarStatusEnum] = Field(None, description="Current status. Options: available, rented, maintenance, retired", example="available")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Toyota Corolla",
                "make": "Toyota",
                "model": "SE",
                "year": 2020,
                "color": "Silver",
                "vin": "1HGBH41JXMN109186",
                "license_plate": "ABC-1234",
                "mileage": 45000,
                "status": "available"
            }
        }


class CarResponse(CarBase):
    """Schema for car response (includes database fields)"""
    id: int = Field(..., description="Unique car identifier")
    created_at: datetime = Field(..., description="Timestamp when car was added")
    updated_at: datetime = Field(..., description="Timestamp when car was last updated")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Toyota Corolla",
                "make": "Toyota",
                "model": "SE",
                "year": 2020,
                "color": "Silver",
                "vin": "1HGBH41JXMN109186",
                "license_plate": "ABC-1234",
                "mileage": 45000,
                "status": "available",
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-15T10:30:00"
            }
        }


# Generic API Response Wrapper
class APIResponse(BaseModel):
    """Generic API response wrapper with status, message, and data"""
    status: bool = Field(..., description="Response status: true for success, false for error")
    message: str = Field(..., description="Human-readable message describing the result")
    data: Optional[Any] = Field(None, description="Response data payload")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": True,
                "message": "Operation completed successfully",
                "data": {}
            }
        }


class CarListData(BaseModel):
    """Data structure for car list response"""
    total: int = Field(..., description="Total number of cars matching the query")
    cars: List[CarResponse] = Field(..., description="List of cars")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total": 2,
                "cars": [
                    {
                        "id": 1,
                        "name": "Toyota Corolla",
                        "make": "Toyota",
                        "model": "SE",
                        "year": 2020,
                        "color": "Silver",
                        "vin": "1HGBH41JXMN109186",
                        "license_plate": "ABC-1234",
                        "mileage": 45000,
                        "status": "available",
                        "created_at": "2024-01-15T10:30:00",
                        "updated_at": "2024-01-15T10:30:00"
                    },
                    {
                        "id": 2,
                        "name": "Honda Civic",
                        "make": "Honda",
                        "model": "LX",
                        "year": 2021,
                        "color": "Black",
                        "vin": "2HGFC2F59MH123456",
                        "license_plate": "XYZ-5678",
                        "mileage": 32000,
                        "status": "rented",
                        "created_at": "2024-01-16T14:20:00",
                        "updated_at": "2024-01-16T14:20:00"
                    }
                ]
            }
        }


class CarListResponse(APIResponse):
    """Schema for list of cars response with standard structure"""
    data: CarListData = Field(..., description="Car list data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": True,
                "message": "Cars retrieved successfully",
                "data": {
                    "total": 2,
                    "cars": [
                        {
                            "id": 1,
                            "name": "Toyota Corolla",
                            "make": "Toyota",
                            "model": "SE",
                            "year": 2020,
                            "color": "Silver",
                            "vin": "1HGBH41JXMN109186",
                            "license_plate": "ABC-1234",
                            "mileage": 45000,
                            "status": "available",
                            "created_at": "2024-01-15T10:30:00",
                            "updated_at": "2024-01-15T10:30:00"
                        }
                    ]
                }
            }
        }


class CarSingleResponse(APIResponse):
    """Schema for single car response with standard structure"""
    data: CarResponse = Field(..., description="Car data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": True,
                "message": "Car retrieved successfully",
                "data": {
                    "id": 1,
                    "name": "Toyota Corolla",
                    "make": "Toyota",
                    "model": "SE",
                    "year": 2020,
                    "color": "Silver",
                    "vin": "1HGBH41JXMN109186",
                    "license_plate": "ABC-1234",
                    "mileage": 45000,
                    "status": "available",
                    "created_at": "2024-01-15T10:30:00",
                    "updated_at": "2024-01-15T10:30:00"
                }
            }
        }


class CarDeleteResponse(APIResponse):
    """Schema for car deletion response with standard structure"""
    data: Optional[Dict[str, Any]] = Field(None, description="Additional data (usually null for delete)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": True,
                "message": "Car deleted successfully",
                "data": None
            }
        }


# Booking CRUD schemas
class BookingStatusEnum(str, Enum):
    """Booking status"""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class BookingBase(BaseModel):
    """Base schema for Booking with common fields"""
    car_id: int = Field(..., description="Car ID for this booking", example=1)
    booking_start_date: datetime = Field(..., description="Booking start date and time", example="2024-01-15T10:00:00")
    booking_end_date: Optional[datetime] = Field(None, description="Booking end date and time (when car is returned)", example="2024-01-20T15:00:00")
    status: BookingStatusEnum = Field(BookingStatusEnum.PENDING, description="Booking status")
    notes: Optional[str] = Field(None, description="Additional notes about the booking", example="Customer requested early pickup")


class BookingCreate(BookingBase):
    """Schema for creating a new booking"""
    class Config:
        json_schema_extra = {
            "example": {
                "car_id": 1,
                "booking_start_date": "2024-01-15T10:00:00",
                "booking_end_date": "2024-01-20T15:00:00",
                "status": "pending",
                "notes": "Customer requested early pickup"
            }
        }


class BookingUpdate(BaseModel):
    """Schema for updating a booking - all fields optional"""
    car_id: Optional[int] = Field(None, description="Car ID", example=1)
    booking_start_date: Optional[datetime] = Field(None, description="Booking start date and time", example="2024-01-15T10:00:00")
    booking_end_date: Optional[datetime] = Field(None, description="Booking end date and time", example="2024-01-20T15:00:00")
    status: Optional[BookingStatusEnum] = Field(None, description="Booking status")
    inspection_id: Optional[str] = Field(None, description="Inspection ID to link to this booking", example="550e8400-e29b-41d4-a716-446655440000")
    notes: Optional[str] = Field(None, description="Additional notes", example="Updated notes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "completed",
                "booking_end_date": "2024-01-20T15:00:00",
                "notes": "Car returned in good condition"
            }
        }


class BookingResponse(BookingBase):
    """Schema for booking response (includes database fields)"""
    id: int = Field(..., description="Unique booking identifier")
    inspection_id: Optional[str] = Field(None, description="Linked inspection ID if available")
    created_at: datetime = Field(..., description="Timestamp when booking was created")
    updated_at: datetime = Field(..., description="Timestamp when booking was last updated")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "car_id": 1,
                "booking_start_date": "2024-01-15T10:00:00",
                "booking_end_date": "2024-01-20T15:00:00",
                "status": "active",
                "inspection_id": "550e8400-e29b-41d4-a716-446655440000",
                "notes": "Customer requested early pickup",
                "created_at": "2024-01-10T08:00:00",
                "updated_at": "2024-01-15T10:00:00"
            }
        }


class BookingListData(BaseModel):
    """Data structure for booking list response"""
    total: int = Field(..., description="Total number of bookings matching the query")
    bookings: List[BookingResponse] = Field(..., description="List of bookings")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total": 2,
                "bookings": []
            }
        }


class BookingListResponse(APIResponse):
    """Schema for list of bookings response with standard structure"""
    data: BookingListData = Field(..., description="Booking list data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": True,
                "message": "Bookings retrieved successfully",
                "data": {
                    "total": 2,
                    "bookings": []
                }
            }
        }


class BookingSingleResponse(APIResponse):
    """Schema for single booking response with standard structure"""
    data: BookingResponse = Field(..., description="Booking data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": True,
                "message": "Booking retrieved successfully",
                "data": {
                    "id": 1,
                    "car_id": 1,
                    "booking_start_date": "2024-01-15T10:00:00",
                    "booking_end_date": "2024-01-20T15:00:00",
                    "status": "active",
                    "inspection_id": None,
                    "notes": "Customer requested early pickup",
                    "created_at": "2024-01-10T08:00:00",
                    "updated_at": "2024-01-15T10:00:00"
                }
            }
        }


class BookingDeleteResponse(APIResponse):
    """Schema for booking deletion response with standard structure"""
    data: Optional[Dict[str, Any]] = Field(None, description="Additional data (usually null for delete)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": True,
                "message": "Booking deleted successfully",
                "data": None
            }
        }


# Booking Image CRUD schemas
class ImageTypeEnum(str, Enum):
    """Image type"""
    BEFORE = "before"
    AFTER = "after"


class BookingImageBase(BaseModel):
    """Base schema for BookingImage with common fields"""
    booking_id: int = Field(..., description="Booking ID this image belongs to", example=1)
    image_type: ImageTypeEnum = Field(..., description="Type of image: before or after", example="before")
    angle: Optional[str] = Field(None, description="Image angle/view (e.g., front, rear, left, right, interior)", example="front")


class BookingImageCreate(BookingImageBase):
    """Schema for creating a new booking image"""
    image_path: str = Field(..., description="Path to the stored image file", example="uploads/2024-01-15/uuid/before_1.jpg")
    
    class Config:
        json_schema_extra = {
            "example": {
                "booking_id": 1,
                "image_type": "before",
                "image_path": "uploads/2024-01-15/uuid/before_1.jpg",
                "angle": "front"
            }
        }


class BookingImageResponse(BookingImageBase):
    """Schema for booking image response (includes database fields)"""
    id: int = Field(..., description="Unique image identifier")
    image_path: str = Field(..., description="Path to the stored image file")
    created_at: datetime = Field(..., description="Timestamp when image was uploaded")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "booking_id": 1,
                "image_type": "before",
                "image_path": "uploads/2024-01-15/uuid/before_1.jpg",
                "angle": "front",
                "created_at": "2024-01-15T10:00:00"
            }
        }


class BookingImageListData(BaseModel):
    """Data structure for booking image list response"""
    total: int = Field(..., description="Total number of images")
    images: List[BookingImageResponse] = Field(..., description="List of images")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total": 2,
                "images": []
            }
        }


class BookingImageListResponse(APIResponse):
    """Schema for list of booking images response with standard structure"""
    data: BookingImageListData = Field(..., description="Booking image list data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": True,
                "message": "Images retrieved successfully",
                "data": {
                    "total": 2,
                    "images": []
                }
            }
        }


class BookingImageSingleResponse(APIResponse):
    """Schema for single booking image response with standard structure"""
    data: BookingImageResponse = Field(..., description="Booking image data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": True,
                "message": "Image retrieved successfully",
                "data": {
                    "id": 1,
                    "booking_id": 1,
                    "image_type": "before",
                    "image_path": "uploads/2024-01-15/uuid/before_1.jpg",
                    "angle": "front",
                    "created_at": "2024-01-15T10:00:00"
                }
            }
        }


class BookingImageDeleteResponse(APIResponse):
    """Schema for booking image deletion response with standard structure"""
    data: Optional[Dict[str, Any]] = Field(None, description="Additional data (usually null for delete)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": True,
                "message": "Image deleted successfully",
                "data": None
            }
        }

