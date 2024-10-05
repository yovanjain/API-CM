from utils.config import get_settings
import urllib.parse
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

settings = get_settings()

# Create a Declarative Meta instance
Base = declarative_base()


encoded_password = urllib.parse.quote_plus(settings.DB_PASSWORD)
URL = f"mysql://{settings.DB_USERNAME}:{encoded_password}@{settings.DB_HOSTNAME}:{settings.DB_PORT}/{settings.DB_SCHEMANAME}"


engine = create_engine(URL)

# DB Dependency
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
