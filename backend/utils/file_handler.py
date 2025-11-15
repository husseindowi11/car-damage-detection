"""
File handling utilities for temporary and permanent file management
"""
import os
import uuid
import logging
from pathlib import Path
from typing import List, Tuple
from datetime import datetime
from fastapi import UploadFile
import aiofiles
import shutil

logger = logging.getLogger(__name__)


class FileHandler:
    """Handles file upload, temporary storage, and permanent storage"""
    
    TEMP_DIR = "temp_images"
    STORAGE_DIR = "uploads"
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    def __init__(self):
        """Initialize file handler and create directories"""
        self.temp_dir = Path(self.TEMP_DIR)
        self.temp_dir.mkdir(exist_ok=True)
        
        self.storage_dir = Path(self.STORAGE_DIR)
        self.storage_dir.mkdir(exist_ok=True)
        
        logger.info(f"Temporary directory: {self.temp_dir.absolute()}")
        logger.info(f"Storage directory: {self.storage_dir.absolute()}")
    
    async def save_temp_file(self, upload_file: UploadFile) -> str:
        """
        Save uploaded file to temporary directory.
        
        Args:
            upload_file: FastAPI UploadFile object
        
        Returns:
            Path to saved temporary file
        """
        try:
            # Generate unique filename
            file_extension = Path(upload_file.filename).suffix.lower()
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = self.temp_dir / unique_filename
            
            logger.info(f"Saving temporary file: {file_path}")
            
            # Save file asynchronously
            async with aiofiles.open(file_path, 'wb') as out_file:
                content = await upload_file.read()
                await out_file.write(content)
            
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Error saving temporary file: {str(e)}")
            raise Exception(f"Failed to save file: {str(e)}")
    
    def cleanup_temp_files(self, file_paths: List[str]) -> None:
        """
        Delete temporary files.
        
        Args:
            file_paths: List of file paths to delete
        """
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Deleted temporary file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to delete file {file_path}: {str(e)}")
    
    def cleanup_all_temp_files(self) -> None:
        """Delete all files in temporary directory"""
        try:
            for file_path in self.temp_dir.glob("*"):
                if file_path.is_file():
                    file_path.unlink()
            logger.info("Cleaned up all temporary files")
        except Exception as e:
            logger.warning(f"Error during cleanup: {str(e)}")
    
    async def save_permanent_files(
        self, 
        before_file: UploadFile, 
        after_file: UploadFile
    ) -> Tuple[str, str, str]:
        """
        Save uploaded files permanently with organized structure.
        
        Files are organized by date and inspection ID:
        uploads/YYYY-MM-DD/inspection_id/before.jpg
        uploads/YYYY-MM-DD/inspection_id/after.jpg
        
        Args:
            before_file: BEFORE image UploadFile
            after_file: AFTER image UploadFile
        
        Returns:
            Tuple of (inspection_id, before_path, after_path)
        """
        try:
            # Generate inspection ID
            inspection_id = str(uuid.uuid4())
            
            # Create date-based directory structure
            date_str = datetime.now().strftime("%Y-%m-%d")
            inspection_dir = self.storage_dir / date_str / inspection_id
            inspection_dir.mkdir(parents=True, exist_ok=True)
            
            # Get file extensions
            before_ext = Path(before_file.filename).suffix.lower() or ".jpg"
            after_ext = Path(after_file.filename).suffix.lower() or ".jpg"
            
            # Define permanent file paths
            before_path = inspection_dir / f"before{before_ext}"
            after_path = inspection_dir / f"after{after_ext}"
            
            logger.info(f"Saving permanent files to: {inspection_dir}")
            
            # Save before image
            # Reset file pointer to beginning
            before_file.file.seek(0)
            async with aiofiles.open(before_path, 'wb') as out_file:
                content = await before_file.read()
                await out_file.write(content)
            
            # Save after image
            # Reset file pointer to beginning
            after_file.file.seek(0)
            async with aiofiles.open(after_path, 'wb') as out_file:
                content = await after_file.read()
                await out_file.write(content)
            
            logger.info(f"Saved permanent files: before={before_path}, after={after_path}")
            
            return inspection_id, str(before_path), str(after_path)
            
        except Exception as e:
            logger.error(f"Error saving permanent files: {str(e)}")
            raise Exception(f"Failed to save permanent files: {str(e)}")
    
    def copy_to_permanent_storage(
        self, 
        temp_before_path: str, 
        temp_after_path: str
    ) -> Tuple[str, str, str]:
        """
        Copy temporary files to permanent storage (single image version).
        
        Args:
            temp_before_path: Path to temporary BEFORE file
            temp_after_path: Path to temporary AFTER file
        
        Returns:
            Tuple of (inspection_id, before_path, after_path)
        """
        try:
            # Generate inspection ID
            inspection_id = str(uuid.uuid4())
            
            # Create date-based directory structure
            date_str = datetime.now().strftime("%Y-%m-%d")
            inspection_dir = self.storage_dir / date_str / inspection_id
            inspection_dir.mkdir(parents=True, exist_ok=True)
            
            # Get file extensions
            before_ext = Path(temp_before_path).suffix
            after_ext = Path(temp_after_path).suffix
            
            # Define permanent file paths
            before_path = inspection_dir / f"before{before_ext}"
            after_path = inspection_dir / f"after{after_ext}"
            
            logger.info(f"Copying files to permanent storage: {inspection_dir}")
            
            # Copy files
            shutil.copy2(temp_before_path, before_path)
            shutil.copy2(temp_after_path, after_path)
            
            logger.info(f"Copied to permanent storage: before={before_path}, after={after_path}")
            
            return inspection_id, str(before_path), str(after_path)
            
        except Exception as e:
            logger.error(f"Error copying to permanent storage: {str(e)}")
            raise Exception(f"Failed to copy to permanent storage: {str(e)}")
    
    def copy_multiple_to_permanent_storage(
        self, 
        temp_before_paths: list[str], 
        temp_after_paths: list[str]
    ) -> Tuple[str, list[str], list[str]]:
        """
        Copy multiple temporary files to permanent storage.
        
        Args:
            temp_before_paths: List of paths to temporary BEFORE files
            temp_after_paths: List of paths to temporary AFTER files
        
        Returns:
            Tuple of (inspection_id, before_paths, after_paths)
        """
        try:
            # Generate inspection ID
            inspection_id = str(uuid.uuid4())
            
            # Create date-based directory structure
            date_str = datetime.now().strftime("%Y-%m-%d")
            inspection_dir = self.storage_dir / date_str / inspection_id
            inspection_dir.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Copying {len(temp_before_paths)} BEFORE and {len(temp_after_paths)} AFTER images to: {inspection_dir}")
            
            # Copy all BEFORE images
            before_paths = []
            for idx, temp_path in enumerate(temp_before_paths, 1):
                ext = Path(temp_path).suffix
                perm_path = inspection_dir / f"before_{idx}{ext}"
                shutil.copy2(temp_path, perm_path)
                # Return relative path from uploads directory for URL construction
                relative_path = perm_path.relative_to(self.storage_dir)
                before_paths.append(str(relative_path).replace('\\', '/'))  # Use forward slashes
                logger.info(f"Copied BEFORE image {idx}: {perm_path}")
            
            # Copy all AFTER images
            after_paths = []
            for idx, temp_path in enumerate(temp_after_paths, 1):
                ext = Path(temp_path).suffix
                perm_path = inspection_dir / f"after_{idx}{ext}"
                shutil.copy2(temp_path, perm_path)
                # Return relative path from uploads directory for URL construction
                relative_path = perm_path.relative_to(self.storage_dir)
                after_paths.append(str(relative_path).replace('\\', '/'))  # Use forward slashes
                logger.info(f"Copied AFTER image {idx}: {perm_path}")
            
            logger.info(f"All images copied to permanent storage: {inspection_dir}")
            
            return inspection_id, before_paths, after_paths
            
        except Exception as e:
            logger.error(f"Error copying to permanent storage: {str(e)}")
            raise Exception(f"Failed to copy to permanent storage: {str(e)}")

