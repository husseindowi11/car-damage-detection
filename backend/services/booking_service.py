"""
CRUD operations for Booking management
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from models.database import Booking, Inspection
from models.schemas import BookingCreate, BookingUpdate
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BookingService:
    """Service class for Booking CRUD operations"""
    
    @staticmethod
    def create_booking(db: Session, booking_data: BookingCreate) -> Booking:
        """
        Create a new booking in the database.
        
        Args:
            db: Database session
            booking_data: Booking data from request
            
        Returns:
            Created booking object
        """
        try:
            db_booking = Booking(
                car_id=booking_data.car_id,
                booking_start_date=booking_data.booking_start_date,
                booking_end_date=booking_data.booking_end_date,
                status=booking_data.status,
                notes=booking_data.notes
            )
            
            db.add(db_booking)
            db.commit()
            db.refresh(db_booking)
            
            logger.info(f"Created new booking: {db_booking.id} for car {db_booking.car_id}")
            return db_booking
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating booking: {str(e)}")
            raise
    
    @staticmethod
    def get_booking(db: Session, booking_id: int) -> Optional[Booking]:
        """
        Get a single booking by ID.
        
        Args:
            db: Database session
            booking_id: Booking ID
            
        Returns:
            Booking object or None if not found
        """
        return db.query(Booking).filter(Booking.id == booking_id).first()
    
    @staticmethod
    def get_bookings(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[str] = None,
        car_id: Optional[int] = None,
        start_date_from: Optional[datetime] = None,
        start_date_to: Optional[datetime] = None
    ) -> List[Booking]:
        """
        Get list of bookings with optional filtering.
        
        Args:
            db: Database session
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return
            status: Filter by booking status
            car_id: Filter by car ID
            start_date_from: Filter bookings starting from this date
            start_date_to: Filter bookings starting until this date
            
        Returns:
            List of booking objects
        """
        query = db.query(Booking)
        
        if status:
            query = query.filter(Booking.status == status)
        if car_id:
            query = query.filter(Booking.car_id == car_id)
        if start_date_from:
            query = query.filter(Booking.booking_start_date >= start_date_from)
        if start_date_to:
            query = query.filter(Booking.booking_start_date <= start_date_to)
        
        return query.order_by(Booking.booking_start_date.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_bookings_count(
        db: Session,
        status: Optional[str] = None,
        car_id: Optional[int] = None,
        start_date_from: Optional[datetime] = None,
        start_date_to: Optional[datetime] = None
    ) -> int:
        """
        Get total count of bookings with optional filtering.
        
        Args:
            db: Database session
            status: Filter by booking status
            car_id: Filter by car ID
            start_date_from: Filter bookings starting from this date
            start_date_to: Filter bookings starting until this date
            
        Returns:
            Total count of bookings
        """
        query = db.query(Booking)
        
        if status:
            query = query.filter(Booking.status == status)
        if car_id:
            query = query.filter(Booking.car_id == car_id)
        if start_date_from:
            query = query.filter(Booking.booking_start_date >= start_date_from)
        if start_date_to:
            query = query.filter(Booking.booking_start_date <= start_date_to)
        
        return query.count()
    
    @staticmethod
    def update_booking(db: Session, booking_id: int, booking_data: BookingUpdate) -> Optional[Booking]:
        """
        Update a booking's information.
        
        Args:
            db: Database session
            booking_id: Booking ID to update
            booking_data: Updated booking data
            
        Returns:
            Updated booking object or None if not found
        """
        try:
            db_booking = db.query(Booking).filter(Booking.id == booking_id).first()
            
            if not db_booking:
                return None
            
            # Update only provided fields
            update_data = booking_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_booking, field, value)
            
            db.commit()
            db.refresh(db_booking)
            
            logger.info(f"Updated booking: {db_booking.id}")
            return db_booking
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating booking {booking_id}: {str(e)}")
            raise
    
    @staticmethod
    def delete_booking(db: Session, booking_id: int) -> bool:
        """
        Delete a booking from the database.
        
        Args:
            db: Database session
            booking_id: Booking ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        try:
            db_booking = db.query(Booking).filter(Booking.id == booking_id).first()
            
            if not db_booking:
                return False
            
            db.delete(db_booking)
            db.commit()
            
            logger.info(f"Deleted booking: {booking_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting booking {booking_id}: {str(e)}")
            raise
    
    @staticmethod
    def get_bookings_by_car(db: Session, car_id: int) -> List[Booking]:
        """
        Get all bookings for a specific car.
        
        Args:
            db: Database session
            car_id: Car ID
            
        Returns:
            List of booking objects for the car
        """
        return db.query(Booking).filter(Booking.car_id == car_id).order_by(Booking.booking_start_date.desc()).all()

