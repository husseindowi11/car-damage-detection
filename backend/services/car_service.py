"""
CRUD operations for Car management
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from models.database import Car
from models.schemas import CarCreate, CarUpdate
import logging

logger = logging.getLogger(__name__)


class CarService:
    """Service class for Car CRUD operations"""
    
    @staticmethod
    def create_car(db: Session, car_data: CarCreate) -> Car:
        """
        Create a new car in the database.
        
        Args:
            db: Database session
            car_data: Car data from request
            
        Returns:
            Created car object
        """
        try:
            db_car = Car(
                name=car_data.name,
                make=car_data.make,
                model=car_data.model,
                year=car_data.year,
                color=car_data.color,
                vin=car_data.vin,
                license_plate=car_data.license_plate,
                mileage=car_data.mileage,
                status=car_data.status
            )
            
            db.add(db_car)
            db.commit()
            db.refresh(db_car)
            
            logger.info(f"Created new car: {db_car.id} - {db_car.name}")
            return db_car
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating car: {str(e)}")
            raise
    
    @staticmethod
    def get_car(db: Session, car_id: int) -> Optional[Car]:
        """
        Get a single car by ID.
        
        Args:
            db: Database session
            car_id: Car ID
            
        Returns:
            Car object or None if not found
        """
        return db.query(Car).filter(Car.id == car_id).first()
    
    @staticmethod
    def get_cars(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[str] = None,
        make: Optional[str] = None,
        year: Optional[int] = None
    ) -> List[Car]:
        """
        Get list of cars with optional filtering.
        
        Args:
            db: Database session
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return
            status: Filter by car status
            make: Filter by car make
            year: Filter by year
            
        Returns:
            List of car objects
        """
        query = db.query(Car)
        
        if status:
            query = query.filter(Car.status == status)
        if make:
            query = query.filter(Car.make.ilike(f"%{make}%"))
        if year:
            query = query.filter(Car.year == year)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_cars_count(
        db: Session,
        status: Optional[str] = None,
        make: Optional[str] = None,
        year: Optional[int] = None
    ) -> int:
        """
        Get total count of cars with optional filtering.
        
        Args:
            db: Database session
            status: Filter by car status
            make: Filter by car make
            year: Filter by year
            
        Returns:
            Total count of cars
        """
        query = db.query(Car)
        
        if status:
            query = query.filter(Car.status == status)
        if make:
            query = query.filter(Car.make.ilike(f"%{make}%"))
        if year:
            query = query.filter(Car.year == year)
        
        return query.count()
    
    @staticmethod
    def update_car(db: Session, car_id: int, car_data: CarUpdate) -> Optional[Car]:
        """
        Update a car's information.
        
        Args:
            db: Database session
            car_id: Car ID to update
            car_data: Updated car data
            
        Returns:
            Updated car object or None if not found
        """
        try:
            db_car = db.query(Car).filter(Car.id == car_id).first()
            
            if not db_car:
                return None
            
            # Update only provided fields
            update_data = car_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_car, field, value)
            
            db.commit()
            db.refresh(db_car)
            
            logger.info(f"Updated car: {db_car.id} - {db_car.name}")
            return db_car
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating car {car_id}: {str(e)}")
            raise
    
    @staticmethod
    def delete_car(db: Session, car_id: int) -> bool:
        """
        Delete a car from the database.
        
        Args:
            db: Database session
            car_id: Car ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        try:
            db_car = db.query(Car).filter(Car.id == car_id).first()
            
            if not db_car:
                return False
            
            db.delete(db_car)
            db.commit()
            
            logger.info(f"Deleted car: {car_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting car {car_id}: {str(e)}")
            raise
    
    @staticmethod
    def get_car_by_vin(db: Session, vin: str) -> Optional[Car]:
        """
        Get a car by VIN (Vehicle Identification Number).
        
        Args:
            db: Database session
            vin: Vehicle Identification Number
            
        Returns:
            Car object or None if not found
        """
        return db.query(Car).filter(Car.vin == vin).first()
    
    @staticmethod
    def get_car_by_license_plate(db: Session, license_plate: str) -> Optional[Car]:
        """
        Get a car by license plate.
        
        Args:
            db: Database session
            license_plate: License plate number
            
        Returns:
            Car object or None if not found
        """
        return db.query(Car).filter(Car.license_plate == license_plate).first()

