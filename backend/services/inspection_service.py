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
        car_name: str,
        car_model: str,
        car_year: int,
        damage_report: Dict[str, Any],
        total_damage_cost: float,
        before_images: List[str],
        after_images: List[str]
    ) -> Inspection:
        """
        Create a new inspection record in the database.
        
        Args:
            db: Database session
            inspection_id: Unique inspection ID (UUID string)
            car_name: Car name
            car_model: Car model/trim
            car_year: Car manufacturing year
            damage_report: Full damage report JSON
            total_damage_cost: Total damage cost
            before_images: List of before image paths
            after_images: List of after image paths
            
        Returns:
            Created inspection object
        """
        try:
            db_inspection = Inspection(
                id=inspection_id,
                car_name=car_name,
                car_model=car_model,
                car_year=car_year,
                damage_report=damage_report,
                total_damage_cost=total_damage_cost,
                before_images=before_images,
                after_images=after_images
            )
            
            db.add(db_inspection)
            db.commit()
            db.refresh(db_inspection)
            
            logger.info(f"Created inspection: {inspection_id} for {car_name} {car_model} {car_year}")
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
    def get_inspections_by_car_name(db: Session, car_name: str) -> List[Inspection]:
        """
        Get all inspections for a specific car name.
        
        Args:
            db: Database session
            car_name: Car name
            
        Returns:
            List of inspection objects
        """
        return db.query(Inspection).filter(Inspection.car_name.ilike(f"%{car_name}%")).order_by(Inspection.created_at.desc()).all()
    
    @staticmethod
    def get_inspections_by_year(db: Session, car_year: int) -> List[Inspection]:
        """
        Get all inspections for a specific car year.
        
        Args:
            db: Database session
            car_year: Car year
            
        Returns:
            List of inspection objects
        """
        return db.query(Inspection).filter(Inspection.car_year == car_year).order_by(Inspection.created_at.desc()).all()

