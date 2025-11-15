"""
SQLAlchemy database models
"""
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Float, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import enum


class CarModel(str, enum.Enum):
    """Predefined car models/trims"""
    SE = "SE"
    GLS = "GLS"
    SPORT = "Sport"
    LX = "LX"
    EX = "EX"
    TOURING = "Touring"
    BASE = "Base"
    PREMIUM = "Premium"
    LUXURY = "Luxury"


class CarStatus(str, enum.Enum):
    """Car status"""
    AVAILABLE = "available"
    RENTED = "rented"
    MAINTENANCE = "maintenance"
    RETIRED = "retired"


class Car(Base):
    """
    Car model for storing vehicle information.
    Used for cost estimation and tracking.
    """
    __tablename__ = "cars"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False, index=True)  # e.g., "Toyota Corolla"
    make = Column(String, nullable=False, index=True)  # e.g., "Toyota"
    model = Column(Enum(CarModel), nullable=False)  # e.g., "SE", "GLS", "Sport"
    year = Column(Integer, nullable=False, index=True)  # e.g., 2020
    color = Column(String, nullable=True)  # e.g., "Silver", "Black"
    vin = Column(String, unique=True, nullable=True, index=True)  # Vehicle Identification Number
    license_plate = Column(String, unique=True, nullable=True, index=True)
    mileage = Column(Integer, nullable=True)  # Current mileage
    status = Column(Enum(CarStatus), default=CarStatus.AVAILABLE, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships (defined after related classes)
    inspections = relationship("Inspection", back_populates="car", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="car", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Car(id={self.id}, name='{self.name}', year={self.year}, model='{self.model}')>"


class BookingStatus(str, enum.Enum):
    """Booking status"""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ImageType(str, enum.Enum):
    """Image type for booking images"""
    BEFORE = "before"
    AFTER = "after"


class BookingImage(Base):
    """
    Booking image model for storing before/after images for bookings.
    Normalized approach - each image is a separate record.
    """
    __tablename__ = "booking_images"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    booking_id = Column(Integer, ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False, index=True)
    image_type = Column(Enum(ImageType), nullable=False, index=True)  # "before" or "after"
    image_path = Column(String, nullable=False)  # Path to the stored image file
    angle = Column(String, nullable=True)  # Optional: "front", "rear", "left", "right", "interior", etc.
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    booking = relationship("Booking", back_populates="images")
    
    def __repr__(self):
        return f"<BookingImage(id={self.id}, booking_id={self.booking_id}, type='{self.image_type}', path='{self.image_path}')>"


class Inspection(Base):
    """
    Inspection model for storing damage assessment results.
    Links to bookings and cars.
    """
    __tablename__ = "inspections"
    
    id = Column(String, primary_key=True, index=True)  # UUID string (inspection_id)
    booking_id = Column(Integer, ForeignKey("bookings.id", ondelete="SET NULL"), nullable=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id", ondelete="CASCADE"), nullable=False, index=True)
    damage_report = Column(JSON, nullable=False)  # Full damage report JSON
    total_damage_cost = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    booking = relationship("Booking", back_populates="inspection", foreign_keys=[booking_id])
    car = relationship("Car", back_populates="inspections")
    
    def __repr__(self):
        return f"<Inspection(id='{self.id}', car_id={self.car_id}, total_cost={self.total_damage_cost})>"


class Booking(Base):
    """
    Booking model for car rental bookings.
    Links to cars and inspections.
    """
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    car_id = Column(Integer, ForeignKey("cars.id", ondelete="CASCADE"), nullable=False, index=True)
    booking_start_date = Column(DateTime, nullable=False, index=True)
    booking_end_date = Column(DateTime, nullable=True, index=True)
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING, nullable=False, index=True)
    inspection_id = Column(String, nullable=True, index=True)  # Reference to inspection (not FK to avoid circular dependency)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    car = relationship("Car", back_populates="bookings")
    inspection = relationship("Inspection", back_populates="booking", uselist=False)
    images = relationship("BookingImage", back_populates="booking", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Booking(id={self.id}, car_id={self.car_id}, status='{self.status}')>"



