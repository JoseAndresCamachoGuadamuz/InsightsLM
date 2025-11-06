import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
from services.config_service import load_config # Imports the function to load our app's configuration

# Load the application configuration to get the user-defined data storage path
config = load_config()
DATA_STORAGE_PATH = config.get("data_storage_path", ".") # Defaults to the current directory if not found

# The database URL is now dynamically created inside the configured data storage path
DATABASE_URL = f"sqlite:///{os.path.join(DATA_STORAGE_PATH, 'insightslm.db')}"

# Create the SQLAlchemy engine, which manages connections to the database.
# The 'connect_args' is needed specifically for SQLite to allow it to be used by multiple threads, as FastAPI runs.
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# A SessionLocal class serves as a factory for new database sessions (i.e., conversations with the DB).
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_db_and_tables():
    """
    Creates the database file and all tables defined in models.py if they don't already exist.
    """
    # Base.metadata contains all the table definitions.
    Base.metadata.create_all(bind=engine)

def get_db():
    """
    A dependency for FastAPI endpoints that provides a database session and ensures it's closed afterward.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()