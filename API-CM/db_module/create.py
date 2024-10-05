from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from models import AuthProfile
from schemas.schemas import CreateUserRequest
from utils.config import get_settings
from utils.services import app_logger 

settings = get_settings()


async def create_new_user(db: Session, user:CreateUserRequest, hashed_password):
    try:
        new_user = AuthProfile(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            password=hashed_password,
            is_active=True,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return True, new_user.auth_profile_id
    except Exception as e:
        db.rollback()
        app_logger.error(f"Create New User | {user.email} | Failed, {str(e)}")
        return False, str(e)
    