"""
Validation utilities for file uploads
"""
import logging
from pathlib import Path
from fastapi import UploadFile, HTTPException

logger = logging.getLogger(__name__)


ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/jpg", 
    "image/png",
    "image/webp"
}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def validate_image_file(file: UploadFile) -> None:
    """
    Validate uploaded image file.
    
    Args:
        file: Uploaded file to validate
    
    Raises:
        ValueError: If file validation fails
    """
    # Check if file exists
    if not file:
        raise ValueError("No file provided")
    
    # Check filename
    if not file.filename:
        raise ValueError("File must have a filename")
    
    # Check file extension
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check MIME type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise ValueError(
            f"Invalid content type: {file.content_type}. "
            f"Allowed types: {', '.join(ALLOWED_MIME_TYPES)}"
        )
    
    logger.info(f"File validation passed: {file.filename}")


def validate_file_size(file_path: str, max_size: int = MAX_FILE_SIZE) -> None:
    """
    Validate file size.
    
    Args:
        file_path: Path to file
        max_size: Maximum allowed size in bytes
    
    Raises:
        ValueError: If file is too large
    """
    import os
    
    file_size = os.path.getsize(file_path)
    
    if file_size > max_size:
        raise ValueError(
            f"File too large: {file_size} bytes. "
            f"Maximum allowed: {max_size} bytes"
        )
    
    logger.info(f"File size OK: {file_size} bytes")

