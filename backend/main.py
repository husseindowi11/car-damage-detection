"""
FastAPI Backend for AI-Powered Vehicle Condition Assessment
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Query, Request
from fastapi.exceptions import RequestValidationError
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
from contextlib import asynccontextmanager
import os
import uuid
import shutil
from pathlib import Path
from typing import Dict, Any
import logging
from dotenv import load_dotenv
from sqlalchemy.orm import Session

# Load environment variables from .env file
load_dotenv()

from services.ai_service import AIService
from services.car_service import CarService
from services.booking_service import BookingService
from services.booking_image_service import BookingImageService
from services.inspection_service import InspectionService
from utils.file_handler import FileHandler
from utils.validators import validate_image_file
from models.schemas import (
    InspectionRequest,
    InspectionResponse,
    HealthResponse,
    RootResponse,
    ErrorResponse,
    CarCreate,
    CarUpdate,
    CarResponse,
    CarListResponse,
    CarSingleResponse,
    CarListData,
    CarDeleteResponse,
    BookingCreate,
    BookingUpdate,
    BookingResponse,
    BookingListResponse,
    BookingSingleResponse,
    BookingListData,
    BookingDeleteResponse,
    BookingImageCreate,
    BookingImageResponse,
    BookingImageListResponse,
    BookingImageSingleResponse,
    BookingImageListData,
    BookingImageDeleteResponse,
    ImageTypeEnum
)
from database import get_db, init_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    # Startup
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized successfully")
    yield
    # Shutdown (if needed in the future)
    logger.info("Application shutting down")


# Initialize FastAPI app
app = FastAPI(
    lifespan=lifespan,
    title="Vehicle Damage Detection API",
    description="""
    AI-powered vehicle condition assessment API for car rental companies.
    
    ## Features
    
    * Compare BEFORE and AFTER vehicle images from multiple angles
    * Detect new damages using Google Gemini Vision AI
    * Generate detailed damage reports with cost estimates
    * Manage fleet of vehicles with comprehensive CRUD operations
    * Save images permanently for record keeping
    
    ## API Response Structure
    
    All Car Management endpoints follow a standard response format:
    
    ```json
    {
      "status": true | false,
      "message": "Human-readable message",
      "data": { /* response payload */ }
    }
    ```
    
    ### Response Fields
    
    - **status**: Operation status (`true` for success, `false` for error)
    - **message**: Human-readable description of the result
    - **data**: Response payload (varies by endpoint)
      - Single car: `CarResponse` object
      - List of cars: `{ total: number, cars: CarResponse[] }`
      - Delete: `null`
      - Error: Additional error details (optional)
    
    ## Endpoints
    
    ### Damage Detection
    * **POST /inspect**: Analyze vehicle images for damage detection (supports multiple angles)
    
    ### Car Management (CRUD)
    * **POST /cars**: Create a new car in the fleet
    * **GET /cars**: List all cars with filtering and pagination
    * **GET /cars/{car_id}**: Get a specific car by ID
    * **PUT /cars/{car_id}**: Update car information
    * **DELETE /cars/{car_id}**: Delete a car from the fleet
    
    ### System
    * **GET /health**: Health check endpoint
    * **GET /**: API information and version
    
    ## Documentation
    
    * **Swagger UI**: Available at `/docs` (interactive API testing)
    * **ReDoc**: Available at `/redoc` (beautiful API documentation)
    * **OpenAPI JSON**: Available at `/openapi.json` (machine-readable schema)
    
    ## Authentication
    
    Currently, the API does not require authentication. In production, implement proper authentication mechanisms.
    
    ## Rate Limiting
    
    The AI service (Gemini) has rate limits:
    - **Free Tier**: 250 requests/day, 10 requests/minute
    - Consider implementing rate limiting for production use
    """,
    version="1.0.0",
    contact={
        "name": "Vehicle Damage Detection API",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT",
    },
    tags_metadata=[
        {
            "name": "inspection",
            "description": "Vehicle damage inspection endpoints using AI vision analysis. Compare before and after images to detect new damages.",
        },
        {
            "name": "cars",
            "description": "Car fleet management CRUD operations. Manage vehicle information for damage assessment and cost estimation.",
        },
        {
            "name": "bookings",
            "description": "Booking management CRUD operations. Manage car rental bookings with before/after images and inspections.",
        },
        {
            "name": "booking-images",
            "description": "Booking image management. Upload and manage before/after images for bookings.",
        },
        {
            "name": "health",
            "description": "System health check and status monitoring endpoints.",
        },
    ],
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services (lazy initialization for AI service to handle missing API key gracefully)
ai_service = None
file_handler = FileHandler()

def get_ai_service():
    """Get or initialize AI service (lazy initialization)"""
    global ai_service
    if ai_service is None:
        try:
            ai_service = AIService()
        except ValueError as e:
            logger.error(f"Failed to initialize AI service: {str(e)}")
            # Return None and let the endpoint handle the error
            return None
    return ai_service


@app.get(
    "/",
    response_model=RootResponse,
    tags=["health"],
    summary="Root endpoint",
    description="Returns basic API information and status"
)
async def root():
    """
    Root endpoint that returns API information.
    
    Returns:
        Basic API information including message, version, and status
    """
    return {
        "message": "Vehicle Damage Detection API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["health"],
    summary="Health check",
    description="Check if the API and AI service are running properly"
)
async def health_check():
    """
    Health check endpoint to verify API and AI service status.
    
    Returns:
        Health status of the service and AI provider
    """
    return {
        "status": "healthy",
        "service": "vehicle-damage-detection",
        "ai_service": "google-gemini-vision"
    }


@app.post(
    "/inspect",
    response_model=InspectionResponse,
    status_code=200,
    tags=["inspection"],
    summary="Inspect vehicle for damage",
    description="Analyze BEFORE and AFTER vehicle images to detect new damages using AI. Images must already be uploaded to the booking via the booking images API.",
    responses={
        200: {
            "description": "Successful inspection",
            "model": InspectionResponse
        },
        400: {
            "description": "No images found for booking or validation error",
            "model": ErrorResponse
        },
        404: {
            "description": "Booking not found",
            "model": ErrorResponse
        },
        500: {
            "description": "Internal server error (AI service unavailable, processing error, etc.)",
            "model": ErrorResponse
        }
    }
)
async def inspect_vehicle(
    request: InspectionRequest,
    db: Session = Depends(get_db)
) -> InspectionResponse:
    """
    Compare BEFORE and AFTER vehicle images from multiple angles to detect new damages.
    
    This endpoint uses AI to analyze vehicle images that are already stored in the booking_images table.
    Images must be uploaded first via the booking images API (POST /bookings/{booking_id}/images).
    
    **Prerequisites:**
    - Booking must exist
    - BEFORE images must be uploaded to the booking via POST /bookings/{booking_id}/images?image_type=before
    - AFTER images must be uploaded to the booking via POST /bookings/{booking_id}/images?image_type=after
    
    **Request Body:**
    ```json
    {
      "booking_id": 1
    }
    ```
    
    **Example:**
    ```bash
    # First upload images (if not already uploaded)
    POST /bookings/1/images?image_type=before
    POST /bookings/1/images?image_type=after
    
    # Then run inspection
    POST /inspect
    Content-Type: application/json
    {
      "booking_id": 1
    }
    ```
    """
    logger.info(f"Received inspection request for booking_id={request.booking_id}")
    
    try:
        # Validate booking exists
        booking = BookingService.get_booking(db, request.booking_id)
        if not booking:
            raise HTTPException(
                status_code=404,
                detail=f"Booking with ID {request.booking_id} not found"
            )
        
        car_id = booking.car_id
        
        # Get images from booking_images table
        from models.database import ImageType
        booking_images = BookingImageService.get_booking_images(db, booking_id=request.booking_id)
        
        before_images = [img for img in booking_images if img.image_type == ImageType.BEFORE]
        after_images = [img for img in booking_images if img.image_type == ImageType.AFTER]
        
        # Validate images exist
        if not before_images:
            raise HTTPException(
                status_code=400,
                detail=f"No BEFORE images found for booking {request.booking_id}. Please upload images first using POST /bookings/{request.booking_id}/images?image_type=before"
            )
        
        if not after_images:
            raise HTTPException(
                status_code=400,
                detail=f"No AFTER images found for booking {request.booking_id}. Please upload images first using POST /bookings/{request.booking_id}/images?image_type=after"
            )
        
        # Get image paths
        before_paths = [img.image_path for img in before_images]
        after_paths = [img.image_path for img in after_images]
        
        logger.info(f"Using {len(before_paths)} BEFORE and {len(after_paths)} AFTER images from booking {request.booking_id}")
        
        # Process images with AI service
        ai_service_instance = get_ai_service()
        if ai_service_instance is None:
            raise HTTPException(
                status_code=500,
                detail="AI service not available. Please configure GEMINI_API_KEY."
            )
        result = await ai_service_instance.analyze_damage(before_paths, after_paths)
        
        # Generate inspection ID
        inspection_id = str(uuid.uuid4())
        
        # Images are already in database, use their paths
        permanent_before_paths = before_paths
        permanent_after_paths = after_paths
        
        # Create inspection record in database
        damage_report = result["report"]
        total_cost = damage_report.get("total_estimated_cost_usd", 0.0)
        InspectionService.create_inspection(
            db,
            inspection_id,
            car_id,
            damage_report,
            total_cost,
            request.booking_id
        )
        
        # Update booking with inspection_id
        from models.schemas import BookingUpdate
        BookingService.update_booking(db, request.booking_id, BookingUpdate(inspection_id=inspection_id))
        
        logger.info(f"Analysis completed successfully. Inspection ID: {inspection_id}")
        
        return {
            "success": True,
            "inspection_id": inspection_id,
            "report": damage_report,
            "saved_images": {
                "before": permanent_before_paths,
                "after": permanent_after_paths
            }
        }
            
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error processing inspection: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process inspection: {str(e)}"
        )


# ============================================================================
# CAR MANAGEMENT ENDPOINTS
# ============================================================================

@app.post(
    "/cars",
    response_model=CarSingleResponse,
    status_code=201,
    tags=["cars"],
    summary="Create a new car",
    description="Add a new car to the fleet database with all relevant vehicle information.",
    responses={
        201: {
            "description": "Car created successfully",
            "model": CarSingleResponse
        },
        400: {
            "description": "Validation error or duplicate VIN/License Plate",
            "model": ErrorResponse
        }
    }
)
def create_car(
    car: CarCreate,
    db: Session = Depends(get_db)
) -> CarSingleResponse:
    """Create a new car in the database"""
    logger.info(f"Creating new car: {car.name}")
    
    try:
        # Check for duplicate VIN or license plate
        if car.vin and CarService.get_car_by_vin(db, car.vin):
            raise HTTPException(
                status_code=400,
                detail=f"Car with VIN {car.vin} already exists"
            )
        
        if car.license_plate and CarService.get_car_by_license_plate(db, car.license_plate):
            raise HTTPException(
                status_code=400,
                detail=f"Car with license plate {car.license_plate} already exists"
            )
        
        # Create the car
        db_car = CarService.create_car(db, car)
        
        return CarSingleResponse(
            status=True,
            message="Car created successfully",
            data=db_car
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating car: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/cars",
    response_model=CarListResponse,
    status_code=200,
    tags=["cars"],
    summary="List all cars",
    description="Get a list of all cars with optional filtering by status, make, and year, with pagination support.",
    responses={
        200: {
            "description": "List of cars retrieved successfully",
            "model": CarListResponse
        }
    }
)
def list_cars(
    skip: int = Query(0, ge=0, description="Number of records to skip (pagination)"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    status: Optional[str] = Query(None, description="Filter by car status"),
    make: Optional[str] = Query(None, description="Filter by car make/manufacturer"),
    year: Optional[int] = Query(None, ge=1900, le=2100, description="Filter by year"),
    db: Session = Depends(get_db)
) -> CarListResponse:
    """Get list of cars with optional filtering"""
    logger.info(f"Listing cars: skip={skip}, limit={limit}, status={status}, make={make}, year={year}")
    
    try:
        cars = CarService.get_cars(db, skip=skip, limit=limit, status=status, make=make, year=year)
        total = CarService.get_cars_count(db, status=status, make=make, year=year)
        
        return CarListResponse(
            status=True,
            message=f"Retrieved {len(cars)} car(s) successfully",
            data=CarListData(total=total, cars=cars)
        )
        
    except Exception as e:
        logger.error(f"Error listing cars: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/cars/{car_id}",
    response_model=CarSingleResponse,
    status_code=200,
    tags=["cars"],
    summary="Get a specific car",
    description="Retrieve detailed information about a specific car by its ID.",
    responses={
        200: {
            "description": "Car retrieved successfully",
            "model": CarSingleResponse
        },
        404: {
            "description": "Car not found",
            "model": ErrorResponse
        }
    }
)
def get_car(
    car_id: int,
    db: Session = Depends(get_db)
) -> CarSingleResponse:
    """Get a single car by ID"""
    logger.info(f"Getting car: {car_id}")
    
    try:
        db_car = CarService.get_car(db, car_id)
        
        if not db_car:
            raise HTTPException(
                status_code=404,
                detail=f"Car with ID {car_id} not found"
            )
        
        return CarSingleResponse(
            status=True,
            message="Car retrieved successfully",
            data=db_car
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting car {car_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put(
    "/cars/{car_id}",
    response_model=CarSingleResponse,
    status_code=200,
    tags=["cars"],
    summary="Update a car",
    description="Update information for an existing car. All fields are optional for partial updates.",
    responses={
        200: {
            "description": "Car updated successfully",
            "model": CarSingleResponse
        },
        404: {
            "description": "Car not found",
            "model": ErrorResponse
        },
        400: {
            "description": "Validation error or duplicate VIN/License Plate",
            "model": ErrorResponse
        }
    }
)
def update_car(
    car_id: int,
    car: CarUpdate,
    db: Session = Depends(get_db)
) -> CarSingleResponse:
    """Update a car's information"""
    logger.info(f"Updating car: {car_id}")
    
    try:
        # Check if car exists
        existing_car = CarService.get_car(db, car_id)
        if not existing_car:
            raise HTTPException(
                status_code=404,
                detail=f"Car with ID {car_id} not found"
            )
        
        # Check for duplicate VIN (if updating VIN)
        if car.vin and car.vin != existing_car.vin:
            duplicate = CarService.get_car_by_vin(db, car.vin)
            if duplicate and duplicate.id != car_id:
                raise HTTPException(
                    status_code=400,
                    detail=f"Car with VIN {car.vin} already exists"
                )
        
        # Check for duplicate license plate (if updating license plate)
        if car.license_plate and car.license_plate != existing_car.license_plate:
            duplicate = CarService.get_car_by_license_plate(db, car.license_plate)
            if duplicate and duplicate.id != car_id:
                raise HTTPException(
                    status_code=400,
                    detail=f"Car with license plate {car.license_plate} already exists"
                )
        
        # Update the car
        updated_car = CarService.update_car(db, car_id, car)
        
        return CarSingleResponse(
            status=True,
            message="Car updated successfully",
            data=updated_car
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating car {car_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete(
    "/cars/{car_id}",
    response_model=CarDeleteResponse,
    status_code=200,
    tags=["cars"],
    summary="Delete a car",
    description="Remove a car from the fleet database. This operation cannot be undone.",
    responses={
        200: {
            "description": "Car deleted successfully",
            "model": CarDeleteResponse
        },
        404: {
            "description": "Car not found",
            "model": ErrorResponse
        }
    }
)
def delete_car(
    car_id: int,
    db: Session = Depends(get_db)
) -> CarDeleteResponse:
    """Delete a car from the database"""
    logger.info(f"Deleting car: {car_id}")
    
    try:
        deleted = CarService.delete_car(db, car_id)
        
        if not deleted:
            raise HTTPException(
                status_code=404,
                detail=f"Car with ID {car_id} not found"
            )
        
        return CarDeleteResponse(
            status=True,
            message="Car deleted successfully",
            data=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting car {car_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# BOOKING MANAGEMENT ENDPOINTS
# ============================================================================

@app.post(
    "/bookings",
    response_model=BookingSingleResponse,
    status_code=201,
    tags=["bookings"],
    summary="Create a new booking",
    description="Create a new car rental booking with start and end dates.",
    responses={
        201: {
            "description": "Booking created successfully",
            "model": BookingSingleResponse
        },
        400: {
            "description": "Validation error or car not found",
            "model": ErrorResponse
        }
    }
)
def create_booking(
    booking: BookingCreate,
    db: Session = Depends(get_db)
) -> BookingSingleResponse:
    """Create a new booking"""
    logger.info(f"Creating new booking for car {booking.car_id}")
    
    try:
        # Validate that car exists
        from services.car_service import CarService
        car = CarService.get_car(db, booking.car_id)
        if not car:
            raise HTTPException(
                status_code=400,
                detail=f"Car with ID {booking.car_id} not found"
            )
        
        # Validate dates
        if booking.booking_end_date and booking.booking_end_date < booking.booking_start_date:
            raise HTTPException(
                status_code=400,
                detail="booking_end_date must be after booking_start_date"
            )
        
        # Create the booking
        db_booking = BookingService.create_booking(db, booking)
        
        return BookingSingleResponse(
            status=True,
            message="Booking created successfully",
            data=db_booking
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating booking: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/bookings",
    response_model=BookingListResponse,
    status_code=200,
    tags=["bookings"],
    summary="List all bookings",
    description="Get a list of all bookings with optional filtering by status, car_id, and date range.",
    responses={
        200: {
            "description": "List of bookings retrieved successfully",
            "model": BookingListResponse
        }
    }
)
def list_bookings(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    status: Optional[str] = Query(None, description="Filter by booking status"),
    car_id: Optional[int] = Query(None, description="Filter by car ID"),
    start_date_from: Optional[datetime] = Query(None, description="Filter bookings starting from this date"),
    start_date_to: Optional[datetime] = Query(None, description="Filter bookings starting until this date"),
    db: Session = Depends(get_db)
) -> BookingListResponse:
    """Get list of bookings with optional filtering"""
    logger.info(f"Listing bookings: skip={skip}, limit={limit}, status={status}, car_id={car_id}")
    
    try:
        bookings = BookingService.get_bookings(
            db, 
            skip=skip, 
            limit=limit, 
            status=status, 
            car_id=car_id,
            start_date_from=start_date_from,
            start_date_to=start_date_to
        )
        total = BookingService.get_bookings_count(
            db, 
            status=status, 
            car_id=car_id,
            start_date_from=start_date_from,
            start_date_to=start_date_to
        )
        
        return BookingListResponse(
            status=True,
            message=f"Retrieved {len(bookings)} booking(s) successfully",
            data=BookingListData(total=total, bookings=bookings)
        )
        
    except Exception as e:
        logger.error(f"Error listing bookings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/bookings/{booking_id}",
    response_model=BookingSingleResponse,
    status_code=200,
    tags=["bookings"],
    summary="Get a specific booking",
    description="Retrieve detailed information about a specific booking by its ID.",
    responses={
        200: {
            "description": "Booking retrieved successfully",
            "model": BookingSingleResponse
        },
        404: {
            "description": "Booking not found",
            "model": ErrorResponse
        }
    }
)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db)
) -> BookingSingleResponse:
    """Get a single booking by ID"""
    logger.info(f"Getting booking: {booking_id}")
    
    try:
        db_booking = BookingService.get_booking(db, booking_id)
        
        if not db_booking:
            raise HTTPException(
                status_code=404,
                detail=f"Booking with ID {booking_id} not found"
            )
        
        return BookingSingleResponse(
            status=True,
            message="Booking retrieved successfully",
            data=db_booking
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting booking {booking_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put(
    "/bookings/{booking_id}",
    response_model=BookingSingleResponse,
    status_code=200,
    tags=["bookings"],
    summary="Update a booking",
    description="Update information for an existing booking. All fields are optional.",
    responses={
        200: {
            "description": "Booking updated successfully",
            "model": BookingSingleResponse
        },
        404: {
            "description": "Booking not found",
            "model": ErrorResponse
        },
        400: {
            "description": "Validation error",
            "model": ErrorResponse
        }
    }
)
def update_booking(
    booking_id: int,
    booking: BookingUpdate,
    db: Session = Depends(get_db)
) -> BookingSingleResponse:
    """Update a booking's information"""
    logger.info(f"Updating booking: {booking_id}")
    
    try:
        # Check if booking exists
        existing_booking = BookingService.get_booking(db, booking_id)
        if not existing_booking:
            raise HTTPException(
                status_code=404,
                detail=f"Booking with ID {booking_id} not found"
            )
        
        # Validate car exists if updating car_id
        if booking.car_id:
            from services.car_service import CarService
            car = CarService.get_car(db, booking.car_id)
            if not car:
                raise HTTPException(
                    status_code=400,
                    detail=f"Car with ID {booking.car_id} not found"
                )
        
        # Validate dates if updating
        start_date = booking.booking_start_date or existing_booking.booking_start_date
        end_date = booking.booking_end_date if booking.booking_end_date is not None else existing_booking.booking_end_date
        
        if end_date and end_date < start_date:
            raise HTTPException(
                status_code=400,
                detail="booking_end_date must be after booking_start_date"
            )
        
        # Validate inspection exists if linking inspection
        if booking.inspection_id:
            from services.inspection_service import InspectionService
            inspection = InspectionService.get_inspection(db, booking.inspection_id)
            if not inspection:
                raise HTTPException(
                    status_code=400,
                    detail=f"Inspection with ID {booking.inspection_id} not found"
                )
        
        # Update the booking
        updated_booking = BookingService.update_booking(db, booking_id, booking)
        
        return BookingSingleResponse(
            status=True,
            message="Booking updated successfully",
            data=updated_booking
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating booking {booking_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete(
    "/bookings/{booking_id}",
    response_model=BookingDeleteResponse,
    status_code=200,
    tags=["bookings"],
    summary="Delete a booking",
    description="Remove a booking from the database. This operation cannot be undone.",
    responses={
        200: {
            "description": "Booking deleted successfully",
            "model": BookingDeleteResponse
        },
        404: {
            "description": "Booking not found",
            "model": ErrorResponse
        }
    }
)
def delete_booking(
    booking_id: int,
    db: Session = Depends(get_db)
) -> BookingDeleteResponse:
    """Delete a booking from the database"""
    logger.info(f"Deleting booking: {booking_id}")
    
    try:
        deleted = BookingService.delete_booking(db, booking_id)
        
        if not deleted:
            raise HTTPException(
                status_code=404,
                detail=f"Booking with ID {booking_id} not found"
            )
        
        return BookingDeleteResponse(
            status=True,
            message="Booking deleted successfully",
            data=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting booking {booking_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# BOOKING IMAGE MANAGEMENT ENDPOINTS
# ============================================================================

@app.post(
    "/bookings/{booking_id}/images",
    response_model=BookingImageListResponse,
    status_code=201,
    tags=["booking-images"],
    summary="Upload images for a booking",
    description="Upload before or after images for a specific booking. Supports multiple images.",
    responses={
        201: {
            "description": "Images uploaded successfully",
            "model": BookingImageListResponse
        },
        400: {
            "description": "Validation error or booking not found",
            "model": ErrorResponse
        }
    }
)
async def upload_booking_images(
    booking_id: int,
    image_type: ImageTypeEnum = Query(..., description="Type of image: before or after"),
    images: List[UploadFile] = File(..., description="Image files to upload"),
    angles: Optional[List[str]] = Query(None, description="Optional list of angles for each image (e.g., front, rear, left, right)"),
    db: Session = Depends(get_db)
) -> BookingImageListResponse:
    """Upload images for a booking"""
    logger.info(f"Uploading {len(images)} {image_type} images for booking {booking_id}")
    
    try:
        # Validate booking exists
        booking = BookingService.get_booking(db, booking_id)
        if not booking:
            raise HTTPException(
                status_code=400,
                detail=f"Booking with ID {booking_id} not found"
            )
        
        # Validate all uploaded files
        for img in images:
            validate_image_file(img)
        
        # Validate angles list length matches images if provided
        if angles and len(angles) != len(images):
            raise HTTPException(
                status_code=400,
                detail="Number of angles must match number of images"
            )
        
        # Save temporary files
        temp_paths = []
        for img in images:
            path = await file_handler.save_temp_file(img)
            temp_paths.append(path)
        
        try:
            # Save images permanently
            inspection_id = str(uuid.uuid4())
            date_str = datetime.now().strftime("%Y-%m-%d")
            inspection_dir = file_handler.storage_dir / date_str / inspection_id
            inspection_dir.mkdir(parents=True, exist_ok=True)
            
            permanent_paths = []
            for idx, temp_path in enumerate(temp_paths):
                ext = Path(temp_path).suffix
                angle_suffix = f"_{angles[idx]}" if angles and idx < len(angles) else f"_{idx+1}"
                perm_path = inspection_dir / f"{image_type}{angle_suffix}{ext}"
                shutil.copy2(temp_path, perm_path)
                permanent_paths.append(str(perm_path))
            
            # Create booking image records
            from models.database import ImageType
            db_image_type = ImageType.BEFORE if image_type == ImageTypeEnum.BEFORE else ImageType.AFTER
            created_images = BookingImageService.create_multiple_booking_images(
                db,
                booking_id,
                permanent_paths,
                db_image_type,
                angles
            )
            
            return BookingImageListResponse(
                status=True,
                message=f"Uploaded {len(created_images)} {image_type} image(s) successfully",
                data=BookingImageListData(total=len(created_images), images=created_images)
            )
            
        finally:
            # Cleanup temporary files
            file_handler.cleanup_temp_files(temp_paths)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading booking images: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/bookings/{booking_id}/images",
    response_model=BookingImageListResponse,
    status_code=200,
    tags=["booking-images"],
    summary="Get all images for a booking",
    description="Retrieve all before and after images for a specific booking, with optional filtering by image type.",
    responses={
        200: {
            "description": "Images retrieved successfully",
            "model": BookingImageListResponse
        },
        404: {
            "description": "Booking not found",
            "model": ErrorResponse
        }
    }
)
def get_booking_images(
    booking_id: int,
    image_type: Optional[ImageTypeEnum] = Query(None, description="Filter by image type: before or after"),
    db: Session = Depends(get_db)
) -> BookingImageListResponse:
    """Get all images for a booking"""
    logger.info(f"Getting images for booking {booking_id}, type={image_type}")
    
    try:
        # Validate booking exists
        booking = BookingService.get_booking(db, booking_id)
        if not booking:
            raise HTTPException(
                status_code=404,
                detail=f"Booking with ID {booking_id} not found"
            )
        
        # Get images
        from models.database import ImageType
        db_image_type = ImageType.BEFORE if image_type == ImageTypeEnum.BEFORE else ImageType.AFTER if image_type == ImageTypeEnum.AFTER else None
        
        images = BookingImageService.get_booking_images(db, booking_id=booking_id, image_type=db_image_type)
        total = BookingImageService.get_booking_images_count(db, booking_id=booking_id, image_type=db_image_type)
        
        return BookingImageListResponse(
            status=True,
            message=f"Retrieved {len(images)} image(s) successfully",
            data=BookingImageListData(total=total, images=images)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting booking images: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/bookings/{booking_id}/images/{image_id}",
    response_model=BookingImageSingleResponse,
    status_code=200,
    tags=["booking-images"],
    summary="Get a specific booking image",
    description="Retrieve detailed information about a specific booking image by its ID.",
    responses={
        200: {
            "description": "Image retrieved successfully",
            "model": BookingImageSingleResponse
        },
        404: {
            "description": "Image not found",
            "model": ErrorResponse
        }
    }
)
def get_booking_image(
    booking_id: int,
    image_id: int,
    db: Session = Depends(get_db)
) -> BookingImageSingleResponse:
    """Get a single booking image by ID"""
    logger.info(f"Getting image {image_id} for booking {booking_id}")
    
    try:
        db_image = BookingImageService.get_booking_image(db, image_id)
        
        if not db_image or db_image.booking_id != booking_id:
            raise HTTPException(
                status_code=404,
                detail=f"Image with ID {image_id} not found for booking {booking_id}"
            )
        
        return BookingImageSingleResponse(
            status=True,
            message="Image retrieved successfully",
            data=db_image
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting booking image {image_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete(
    "/bookings/{booking_id}/images/{image_id}",
    response_model=BookingImageDeleteResponse,
    status_code=200,
    tags=["booking-images"],
    summary="Delete a booking image",
    description="Remove a specific image from a booking. This operation cannot be undone.",
    responses={
        200: {
            "description": "Image deleted successfully",
            "model": BookingImageDeleteResponse
        },
        404: {
            "description": "Image not found",
            "model": ErrorResponse
        }
    }
)
def delete_booking_image(
    booking_id: int,
    image_id: int,
    db: Session = Depends(get_db)
) -> BookingImageDeleteResponse:
    """Delete a booking image"""
    logger.info(f"Deleting image {image_id} for booking {booking_id}")
    
    try:
        # Verify image belongs to booking
        db_image = BookingImageService.get_booking_image(db, image_id)
        if not db_image or db_image.booking_id != booking_id:
            raise HTTPException(
                status_code=404,
                detail=f"Image with ID {image_id} not found for booking {booking_id}"
            )
        
        deleted = BookingImageService.delete_booking_image(db, image_id)
        
        if not deleted:
            raise HTTPException(
                status_code=404,
                detail=f"Image with ID {image_id} not found"
            )
        
        return BookingImageDeleteResponse(
            status=True,
            message="Image deleted successfully",
            data=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting booking image {image_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP exception handler - returns standardized error format"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": False,
            "message": exc.detail,
            "data": {
                "error_type": "HTTPException",
                "status_code": exc.status_code
            }
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Validation exception handler - returns standardized error format"""
    errors = exc.errors()
    error_messages = [f"{err['loc']}: {err['msg']}" for err in errors]
    return JSONResponse(
        status_code=422,
        content={
            "status": False,
            "message": f"Validation error: {'; '.join(error_messages)}",
            "data": {
                "error_type": "ValidationError",
                "errors": errors
            }
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler - returns standardized error format"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "status": False,
            "message": f"Internal server error: {str(exc)}",
            "data": {
                "error_type": "InternalServerError",
                "detail": str(exc)
            }
        }
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)



