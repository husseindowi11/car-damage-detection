"""
SQLAlchemy database models
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, JSON
from datetime import datetime
from database import Base


class Inspection(Base):
    """
    Inspection model for storing damage assessment results.
    Stores car information directly and image paths.
    """
    __tablename__ = "inspections"
    
    id = Column(String, primary_key=True, index=True)  # UUID string (inspection_id)
    car_name = Column(String, nullable=False, index=True)  # e.g., "Toyota Corolla"
    car_model = Column(String, nullable=False, index=True)  # e.g., "SE", "GLS", "Sport"
    car_year = Column(Integer, nullable=False, index=True)  # e.g., 2020
    damage_report = Column(JSON, nullable=False)  # Full damage report JSON
    total_damage_cost = Column(Float, nullable=False, default=0.0)
    before_images = Column(JSON, nullable=False)  # Array of image paths
    after_images = Column(JSON, nullable=False)  # Array of image paths
    bounded_images = Column(JSON, nullable=True, default=lambda: [])  # Array of bounded image paths (only if damages exist)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Inspection(id='{self.id}', car_name='{self.car_name}', year={self.car_year}, total_cost={self.total_damage_cost})>"



