"""
Database connection and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# SQLite database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./car_damage_detection.db")

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def get_db():
    """
    Dependency function to get database session.
    Yields a database session and closes it after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database by creating all tables.
    Call this on application startup.
    """
    import logging
    from sqlalchemy import inspect as sqlalchemy_inspect, text
    
    logger = logging.getLogger(__name__)
    logger.info(f"Creating database tables for {DATABASE_URL}...")
    
    # Import all models here so that Base has them before creating tables
    from models.database import Car, Booking, Inspection, BookingImage  # noqa
    
    # Check if inspections table exists and has old columns
    inspector = sqlalchemy_inspect(engine)
    if inspector.has_table("inspections"):
        # Check if old columns exist
        columns = [col['name'] for col in inspector.get_columns("inspections")]
        if 'before_images' in columns or 'after_images' in columns:
            logger.info("Detected old schema with before_images/after_images columns. Migrating...")
            # SQLite doesn't support DROP COLUMN, so we need to recreate the table
            with engine.begin() as conn:  # begin() handles transaction automatically
                try:
                    # Create new table without old columns
                    conn.execute(text("""
                        CREATE TABLE inspections_new (
                            id VARCHAR NOT NULL,
                            booking_id INTEGER,
                            car_id INTEGER NOT NULL,
                            damage_report JSON NOT NULL,
                            total_damage_cost FLOAT NOT NULL,
                            created_at DATETIME NOT NULL,
                            PRIMARY KEY (id),
                            FOREIGN KEY(booking_id) REFERENCES bookings (id) ON DELETE SET NULL,
                            FOREIGN KEY(car_id) REFERENCES cars (id) ON DELETE CASCADE
                        )
                    """))
                    
                    # Copy data (excluding old columns)
                    conn.execute(text("""
                        INSERT INTO inspections_new (id, booking_id, car_id, damage_report, total_damage_cost, created_at)
                        SELECT id, booking_id, car_id, damage_report, total_damage_cost, created_at
                        FROM inspections
                    """))
                    
                    # Drop old table
                    conn.execute(text("DROP TABLE inspections"))
                    
                    # Rename new table
                    conn.execute(text("ALTER TABLE inspections_new RENAME TO inspections"))
                    
                    # Recreate indexes
                    conn.execute(text("CREATE INDEX ix_inspections_booking_id ON inspections (booking_id)"))
                    conn.execute(text("CREATE INDEX ix_inspections_car_id ON inspections (car_id)"))
                    conn.execute(text("CREATE INDEX ix_inspections_id ON inspections (id)"))
                    
                    logger.info("Migration completed: removed before_images and after_images columns")
                except Exception as e:
                    logger.error(f"Migration failed: {str(e)}")
                    raise
    
    # Create all tables (will skip existing ones)
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created (or already exist).")

