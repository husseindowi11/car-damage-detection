"""
CRUD operations for BookingImage management
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from models.database import BookingImage, ImageType
from models.schemas import BookingImageCreate
import logging

logger = logging.getLogger(__name__)


class BookingImageService:
    """Service class for BookingImage CRUD operations"""
    
    @staticmethod
    def create_booking_image(
        db: Session,
        booking_id: int,
        image_type: ImageType,
        image_path: str,
        angle: Optional[str] = None
    ) -> BookingImage:
        """
        Create a new booking image record in the database.
        
        Args:
            db: Database session
            booking_id: Booking ID
            image_type: Type of image (before or after)
            image_path: Path to the stored image file
            angle: Optional angle/view description
            
        Returns:
            Created booking image object
        """
        try:
            db_image = BookingImage(
                booking_id=booking_id,
                image_type=image_type,
                image_path=image_path,
                angle=angle
            )
            
            db.add(db_image)
            db.commit()
            db.refresh(db_image)
            
            logger.info(f"Created booking image: {db_image.id} for booking {booking_id}")
            return db_image
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating booking image: {str(e)}")
            raise
    
    @staticmethod
    def create_multiple_booking_images(
        db: Session,
        booking_id: int,
        image_paths: List[str],
        image_type: ImageType,
        angles: Optional[List[str]] = None
    ) -> List[BookingImage]:
        """
        Create multiple booking image records at once.
        
        Args:
            db: Database session
            booking_id: Booking ID
            image_paths: List of image file paths
            image_type: Type of images (before or after)
            angles: Optional list of angles (must match length of image_paths)
            
        Returns:
            List of created booking image objects
        """
        try:
            images = []
            for idx, image_path in enumerate(image_paths):
                angle = angles[idx] if angles and idx < len(angles) else None
                db_image = BookingImage(
                    booking_id=booking_id,
                    image_type=image_type,
                    image_path=image_path,
                    angle=angle
                )
                db.add(db_image)
                images.append(db_image)
            
            db.commit()
            for img in images:
                db.refresh(img)
            
            logger.info(f"Created {len(images)} booking images for booking {booking_id}")
            return images
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating multiple booking images: {str(e)}")
            raise
    
    @staticmethod
    def get_booking_image(db: Session, image_id: int) -> Optional[BookingImage]:
        """
        Get a single booking image by ID.
        
        Args:
            db: Database session
            image_id: Image ID
            
        Returns:
            Booking image object or None if not found
        """
        return db.query(BookingImage).filter(BookingImage.id == image_id).first()
    
    @staticmethod
    def get_booking_images(
        db: Session,
        booking_id: Optional[int] = None,
        image_type: Optional[ImageType] = None
    ) -> List[BookingImage]:
        """
        Get list of booking images with optional filtering.
        
        Args:
            db: Database session
            booking_id: Filter by booking ID
            image_type: Filter by image type (before or after)
            
        Returns:
            List of booking image objects
        """
        query = db.query(BookingImage)
        
        if booking_id:
            query = query.filter(BookingImage.booking_id == booking_id)
        if image_type:
            query = query.filter(BookingImage.image_type == image_type)
        
        return query.order_by(BookingImage.created_at.asc()).all()
    
    @staticmethod
    def get_booking_images_count(
        db: Session,
        booking_id: Optional[int] = None,
        image_type: Optional[ImageType] = None
    ) -> int:
        """
        Get total count of booking images with optional filtering.
        
        Args:
            db: Database session
            booking_id: Filter by booking ID
            image_type: Filter by image type
            
        Returns:
            Total count of images
        """
        query = db.query(BookingImage)
        
        if booking_id:
            query = query.filter(BookingImage.booking_id == booking_id)
        if image_type:
            query = query.filter(BookingImage.image_type == image_type)
        
        return query.count()
    
    @staticmethod
    def delete_booking_image(db: Session, image_id: int) -> bool:
        """
        Delete a booking image from the database.
        
        Args:
            db: Database session
            image_id: Image ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        try:
            db_image = db.query(BookingImage).filter(BookingImage.id == image_id).first()
            
            if not db_image:
                return False
            
            db.delete(db_image)
            db.commit()
            
            logger.info(f"Deleted booking image: {image_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting booking image {image_id}: {str(e)}")
            raise
    
    @staticmethod
    def delete_booking_images_by_booking(db: Session, booking_id: int) -> int:
        """
        Delete all images for a specific booking.
        
        Args:
            db: Database session
            booking_id: Booking ID
            
        Returns:
            Number of images deleted
        """
        try:
            deleted_count = db.query(BookingImage).filter(BookingImage.booking_id == booking_id).delete()
            db.commit()
            
            logger.info(f"Deleted {deleted_count} images for booking {booking_id}")
            return deleted_count
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting images for booking {booking_id}: {str(e)}")
            raise

