from utils.config import Settings
from models import CompanyProfile
import pandas as pd
from datetime import datetime
from db_module.connection import get_db
from fastapi import Depends
from sqlalchemy.orm import Session

settings = Settings()

async def process_csv_in_background(file_path: str, db: Session = next(get_db())):
    try:
        chunksize = 10**6  # 1 million rows at a time
        for chunk in pd.read_csv(file_path, chunksize=chunksize):
            for index, row in chunk.iterrows():
                # Create a new user record
                user_data = CompanyProfile(
                    first_name=row['first_name'],
                    last_name=row['last_name'],
                    email=row['email'],
                    mobile_number=row['mobile_number'],
                    city=row['city'],
                    state=row['state'],
                    country=row['country'],
                    industry=row['industry'],
                    year_founded=row['year_founded'],
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    is_active=True
                )
                db.add(user_data)
            db.commit()  
    except Exception as e:
        traceback.print_exc()  # Log the error
        raise RuntimeError(f"Error processing the file: {e}")

