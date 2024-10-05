from .database import engine # type: ignore
from models import Base

# Create all tables in the database
Base.metadata.create_all(bind=engine)
