"""
FastAPI Backend for AI-Powered Vehicle Condition Assessment
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Form, Query
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
import logging
from dotenv import load_dotenv
from sqlalchemy.orm import Session

# Load environment variables from .env file
load_dotenv()

from services.ai_service import AIService
from services.inspection_service import InspectionService
from utils.file_handler import FileHandler
from utils.validators import validate_image_file
from models.schemas import (
    InspectionResponse,
    InspectionListResponse,
    InspectionDetailResponse,
    HealthResponse,
    RootResponse,
    ErrorResponse
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
    * Save images permanently for record keeping
    
    ## Endpoints
    
    ### Damage Detection
    * **POST /inspect**: Analyze vehicle images for damage detection (supports multiple angles)
    
    ### System
    * **GET /health**: Health check endpoint
    * **GET /**: API information and version
    
    ## Documentation
    
    * **Swagger UI**: Available at `/docs` (interactive API testing)
    * **ReDoc**: Available at `/redoc` (beautiful API documentation)
    * **OpenAPI JSON**: Available at `/openapi.json` (machine-readable schema)
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
    description="Analyze BEFORE and AFTER vehicle images to detect new damages using AI. Accepts car information and images directly.",
    responses={
        200: {
            "description": "Successful inspection",
            "model": InspectionResponse
        },
        400: {
            "description": "Validation error (invalid file type, missing files, etc.)",
            "model": ErrorResponse
        },
        500: {
            "description": "Internal server error (AI service unavailable, processing error, etc.)",
            "model": ErrorResponse
        }
    }
)
async def inspect_vehicle(
    car_name: str = Form(..., description="Car name (e.g., 'Toyota Corolla', 'Honda Civic')"),
    car_model: str = Form(..., description="Car model/trim (e.g., 'SE', 'GLS', 'Sport')"),
    car_year: int = Form(..., description="Manufacturing year (1900-2100)", ge=1900, le=2100),
    before: List[UploadFile] = File(..., description="Vehicle images at pickup (BEFORE) from multiple angles. Supported formats: JPEG, PNG, WEBP. Max size: 10MB per image"),
    after: List[UploadFile] = File(..., description="Vehicle images at return (AFTER) from multiple angles. Supported formats: JPEG, PNG, WEBP. Max size: 10MB per image"),
    db: Session = Depends(get_db)
) -> InspectionResponse:
    """
    Compare BEFORE and AFTER vehicle images from multiple angles to detect new damages.
    
    This endpoint accepts car information and images directly, processes them with AI,
    and stores the inspection results in the database.
    """
    logger.info(f"Received inspection request: {car_name} {car_model} {car_year}, {len(before)} BEFORE, {len(after)} AFTER images")
    
    try:
        # Validate all uploaded files
        for img in before:
            validate_image_file(img)
        for img in after:
            validate_image_file(img)
        
        logger.info(f"Processing BEFORE images: {[img.filename for img in before]}")
        logger.info(f"Processing AFTER images: {[img.filename for img in after]}")
        
        # Save temporary files for processing
        before_paths = []
        after_paths = []
        
        for img in before:
            path = await file_handler.save_temp_file(img)
            before_paths.append(path)
        
        for img in after:
            path = await file_handler.save_temp_file(img)
            after_paths.append(path)
        
        try:
            # Process images with AI service
            ai_service_instance = get_ai_service()
            if ai_service_instance is None:
                raise HTTPException(
                    status_code=500,
                    detail="AI service not available. Please configure GEMINI_API_KEY."
                )
            result = await ai_service_instance.analyze_damage(before_paths, after_paths)
            
            # Save images permanently to local storage
            inspection_id, permanent_before_paths, permanent_after_paths = (
                file_handler.copy_multiple_to_permanent_storage(before_paths, after_paths)
            )
            
            # Create inspection record in database
            damage_report = result["report"]
            total_cost = damage_report.get("total_estimated_cost_usd", 0.0)
            InspectionService.create_inspection(
                db,
                inspection_id,
                car_name,
                car_model,
                car_year,
                damage_report,
                total_cost,
                permanent_before_paths,
                permanent_after_paths
            )
            
            logger.info(f"Analysis completed successfully. Inspection ID: {inspection_id}")
            
            return {
                "success": True,
                "inspection_id": inspection_id,
                "car_name": car_name,
                "car_model": car_model,
                "car_year": car_year,
                "report": damage_report,
                "saved_images": {
                    "before": permanent_before_paths,
                    "after": permanent_after_paths
                }
            }
            
        finally:
            # Cleanup temporary files (permanent copies are already saved)
            all_temp_paths = before_paths + after_paths
            file_handler.cleanup_temp_files(all_temp_paths)
            
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error processing inspection: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process inspection: {str(e)}"
        )


@app.get(
    "/inspections",
    response_model=InspectionListResponse,
    status_code=200,
    tags=["inspection"],
    summary="List inspections",
    description="Get a list of all inspections with pagination support",
    responses={
        200: {
            "description": "Successful response",
            "model": InspectionListResponse
        },
        500: {
            "description": "Internal server error",
            "model": ErrorResponse
        }
    }
)
async def list_inspections(
    skip: int = Query(0, ge=0, description="Number of records to skip (for pagination)"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
) -> InspectionListResponse:
    """
    Retrieve a paginated list of all inspections.
    
    Returns inspections ordered by creation date (newest first).
    """
    try:
        inspections = InspectionService.get_all_inspections(db, skip=skip, limit=limit)
        total = InspectionService.count_inspections(db)
        
        # Convert to list items (summary format)
        inspection_items = []
        for inspection in inspections:
            inspection_items.append({
                "id": inspection.id,
                "car_name": inspection.car_name,
                "car_model": inspection.car_model,
                "car_year": inspection.car_year,
                "total_damage_cost": inspection.total_damage_cost,
                "created_at": inspection.created_at.isoformat() if inspection.created_at else ""
            })
        
        return {
            "status": True,
            "message": "Inspections retrieved successfully",
            "data": {
                "total": total,
                "inspections": inspection_items
            }
        }
        
    except Exception as e:
        logger.error(f"Error retrieving inspections: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve inspections: {str(e)}"
        )


@app.get(
    "/inspections/{inspection_id}",
    response_model=InspectionDetailResponse,
    status_code=200,
    tags=["inspection"],
    summary="Get inspection details",
    description="Retrieve detailed information about a specific inspection",
    responses={
        200: {
            "description": "Successful response",
            "model": InspectionDetailResponse
        },
        404: {
            "description": "Inspection not found",
            "model": ErrorResponse
        },
        500: {
            "description": "Internal server error",
            "model": ErrorResponse
        }
    }
)
async def get_inspection_details(
    inspection_id: str,
    db: Session = Depends(get_db)
) -> InspectionDetailResponse:
    """
    Retrieve detailed information about a specific inspection by ID.
    
    Returns the full inspection record including damage report and image paths.
    """
    try:
        inspection = InspectionService.get_inspection(db, inspection_id)
        
        if inspection is None:
            raise HTTPException(
                status_code=404,
                detail=f"Inspection with ID '{inspection_id}' not found"
            )
        
        # Convert to detail format
        inspection_detail = {
            "id": inspection.id,
            "car_name": inspection.car_name,
            "car_model": inspection.car_model,
            "car_year": inspection.car_year,
            "damage_report": inspection.damage_report,
            "total_damage_cost": inspection.total_damage_cost,
            "before_images": inspection.before_images if isinstance(inspection.before_images, list) else [],
            "after_images": inspection.after_images if isinstance(inspection.after_images, list) else [],
            "created_at": inspection.created_at.isoformat() if inspection.created_at else ""
        }
        
        return {
            "status": True,
            "message": "Inspection retrieved successfully",
            "data": inspection_detail
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving inspection {inspection_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve inspection: {str(e)}"
        )


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
    """Request validation exception handler - returns standardized error format"""
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
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port)
