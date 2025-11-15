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
    from models.database import Inspection  # noqa
    
    # Check if inspections table exists and needs migration
    inspector = sqlalchemy_inspect(engine)
    if inspector.has_table("inspections"):
        # Check if old columns exist (from previous schema)
        columns = [col['name'] for col in inspector.get_columns("inspections")]
        needs_migration = False
        
        # Check if it has old schema (booking_id, car_id) or missing new fields (car_name, car_model, car_year, before_images, after_images)
        if 'booking_id' in columns or 'car_id' in columns or 'car_name' not in columns:
            needs_migration = True
        
        if needs_migration:
            logger.info("Detected old schema. Migrating inspections table...")
            # SQLite doesn't support DROP COLUMN, so we need to recreate the table
            with engine.begin() as conn:  # begin() handles transaction automatically
                try:
                    # Create new table with new schema
                    conn.execute(text("""
                        CREATE TABLE inspections_new (
                            id VARCHAR NOT NULL,
                            car_name VARCHAR NOT NULL,
                            car_model VARCHAR NOT NULL,
                            car_year INTEGER NOT NULL,
                            damage_report JSON NOT NULL,
                            total_damage_cost FLOAT NOT NULL,
                            before_images JSON NOT NULL,
                            after_images JSON NOT NULL,
                            created_at DATETIME NOT NULL,
                            PRIMARY KEY (id)
                        )
                    """))
                    
                    # Try to copy data if possible (may fail if old schema is incompatible)
                    try:
                        # If old table has damage_report and total_damage_cost, try to preserve them
                        conn.execute(text("""
                            INSERT INTO inspections_new (id, car_name, car_model, car_year, damage_report, total_damage_cost, before_images, after_images, created_at)
                            SELECT 
                                id,
                                'Unknown' as car_name,
                                'Unknown' as car_model,
                                2000 as car_year,
                                COALESCE(damage_report, '{}') as damage_report,
                                COALESCE(total_damage_cost, 0.0) as total_damage_cost,
                                '[]' as before_images,
                                '[]' as after_images,
                                COALESCE(created_at, datetime('now')) as created_at
                            FROM inspections
                        """))
                        logger.info("Migrated existing inspection data")
                    except Exception as e:
                        logger.warning(f"Could not migrate existing data: {str(e)}. Creating fresh table.")
                    
                    # Drop old table
                    conn.execute(text("DROP TABLE inspections"))
                    
                    # Rename new table
                    conn.execute(text("ALTER TABLE inspections_new RENAME TO inspections"))
                    
                    # Recreate indexes
                    conn.execute(text("CREATE INDEX ix_inspections_car_name ON inspections (car_name)"))
                    conn.execute(text("CREATE INDEX ix_inspections_car_model ON inspections (car_model)"))
                    conn.execute(text("CREATE INDEX ix_inspections_car_year ON inspections (car_year)"))
                    conn.execute(text("CREATE INDEX ix_inspections_id ON inspections (id)"))
                    
                    logger.info("Migration completed: updated inspections table schema")
                except Exception as e:
                    logger.error(f"Migration failed: {str(e)}")
                    raise
    
    # Create all tables (will skip existing ones)
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created (or already exist).")

