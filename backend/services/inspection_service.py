"""
CRUD operations for Inspection management
"""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from models.database import Inspection
import logging

logger = logging.getLogger(__name__)


class InspectionService:
    """Service class for Inspection CRUD operations"""
    
    @staticmethod
    def create_inspection(
        db: Session,
        inspection_id: str,
        car_id: int,
        damage_report: Dict[str, Any],
        total_damage_cost: float,
        booking_id: Optional[int] = None
    ) -> Inspection:
        """
        Create a new inspection record in the database.
        
        Args:
            db: Database session
            inspection_id: Unique inspection ID (UUID string)
            car_id: Car ID
            damage_report: Full damage report JSON
            total_damage_cost: Total damage cost
            booking_id: Optional booking ID to link
            
        Returns:
            Created inspection object
        """
        try:
            db_inspection = Inspection(
                id=inspection_id,
                booking_id=booking_id,
                car_id=car_id,
                damage_report=damage_report,
                total_damage_cost=total_damage_cost
            )
            
            db.add(db_inspection)
            db.commit()
            db.refresh(db_inspection)
            
            logger.info(f"Created inspection: {inspection_id} for car {car_id}")
            return db_inspection
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating inspection: {str(e)}")
            raise
    
    @staticmethod
    def get_inspection(db: Session, inspection_id: str) -> Optional[Inspection]:
        """
        Get a single inspection by ID.
        
        Args:
            db: Database session
            inspection_id: Inspection ID (UUID string)
            
        Returns:
            Inspection object or None if not found
        """
        return db.query(Inspection).filter(Inspection.id == inspection_id).first()
    
    @staticmethod
    def get_inspections_by_car(db: Session, car_id: int) -> List[Inspection]:
        """
        Get all inspections for a specific car.
        
        Args:
            db: Database session
            car_id: Car ID
            
        Returns:
            List of inspection objects
        """
        return db.query(Inspection).filter(Inspection.car_id == car_id).order_by(Inspection.created_at.desc()).all()
    
    @staticmethod
    def get_inspections_by_booking(db: Session, booking_id: int) -> List[Inspection]:
        """
        Get all inspections for a specific booking.
        
        Args:
            db: Database session
            booking_id: Booking ID
            
        Returns:
            List of inspection objects
        """
        return db.query(Inspection).filter(Inspection.booking_id == booking_id).order_by(Inspection.created_at.desc()).all()

