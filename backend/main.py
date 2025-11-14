"""
FastAPI Backend for AI-Powered Vehicle Condition Assessment
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from typing import Dict, Any
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from services.ai_service import AIService
from utils.file_handler import FileHandler
from utils.validators import validate_image_file
from models.schemas import (
    InspectionResponse,
    HealthResponse,
    RootResponse,
    ErrorResponse
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Vehicle Damage Detection API",
    description="""
    AI-powered vehicle condition assessment API for car rental companies.
    
    ## Features
    
    * Compare BEFORE and AFTER vehicle images
    * Detect new damages using Google Gemini Vision AI
    * Generate detailed damage reports with cost estimates
    * Save images permanently for record keeping
    
    ## Endpoints
    
    * **POST /inspect**: Analyze vehicle images for damage detection
    * **GET /health**: Health check endpoint
    * **GET /**: API information
    
    ## Documentation
    
    * **Swagger UI**: Available at `/docs`
    * **ReDoc**: Available at `/redoc`
    * **OpenAPI JSON**: Available at `/openapi.json`
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
            "description": "Vehicle damage inspection endpoints. Upload BEFORE and AFTER images to detect new damages.",
        },
        {
            "name": "health",
            "description": "Health check and status endpoints.",
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
    description="""
    Compare BEFORE and AFTER vehicle images from multiple angles to detect new damages.
    
    This endpoint:
    1. Accepts multiple image files for BEFORE (pickup) and AFTER (return) states
    2. Supports multiple angles: front, rear, left side, right side, interior, etc.
    3. Validates all image formats
    4. Processes all images using Google Gemini Vision AI
    5. Cross-references all angles to detect only NEW damages
    6. Generates a comprehensive damage report with cost estimates
    7. Saves all images permanently for record keeping
    8. Returns complete damage report with all saved image paths
    
    **Supported image formats:** JPEG, PNG, WEBP
    **Maximum file size:** 10MB per image
    **Recommended:** Upload 4-6 images per state (before/after) covering all angles
    """,
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
    before: List[UploadFile] = File(
        ...,
        description="Vehicle images at pickup (BEFORE) from multiple angles. Supported formats: JPEG, PNG, WEBP. Max size: 10MB per image"
    ),
    after: List[UploadFile] = File(
        ...,
        description="Vehicle images at return (AFTER) from multiple angles. Supported formats: JPEG, PNG, WEBP. Max size: 10MB per image"
    )
) -> InspectionResponse:
    """
    Compare BEFORE and AFTER vehicle images from multiple angles to detect new damages.
    
    This endpoint uses AI to analyze vehicle images from multiple angles and detect 
    only NEW damages that occurred between pickup and return. It ignores pre-existing 
    damage visible in the BEFORE images.
    
    **Request:**
    - Upload multiple image files via multipart/form-data
    - `before`: List of images of vehicle at pickup (multiple angles)
    - `after`: List of images of vehicle at return (multiple angles)
    - Recommended: front, rear, left side, right side views minimum
    
    **Response:**
    - Comprehensive damage report with detailed analysis
    - Inspection ID and all saved image paths
    
    **Example:**
    ```bash
    curl -X POST "http://localhost:8000/inspect" \\
      -F "before=@before_front.jpg" \\
      -F "before=@before_rear.jpg" \\
      -F "before=@before_left.jpg" \\
      -F "before=@before_right.jpg" \\
      -F "after=@after_front.jpg" \\
      -F "after=@after_rear.jpg" \\
      -F "after=@after_left.jpg" \\
      -F "after=@after_right.jpg"
    ```
    """
    logger.info(f"Received inspection request with {len(before)} BEFORE and {len(after)} AFTER images")
    
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
            
            logger.info(f"Analysis completed successfully. Inspection ID: {inspection_id}")
            
            return {
                "success": True,
                "inspection_id": inspection_id,
                "report": result["report"],
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


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)



