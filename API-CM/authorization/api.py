import traceback
from jose import jwt, JWTError
from fastapi import APIRouter, HTTPException
from models import AuthProfile
from utils.config import get_settings
from sqlalchemy.exc import IntegrityError
from fastapi.params import Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from db_module.connection import get_db
from db_module.create import create_new_user
from schemas.schemas import (
    CreateUserRequest,
    UserLoginRequest,
    HashSlugRequest
)
from utils.services import app_logger
from passlib.context import CryptContext

settings = get_settings()

pwd_context = CryptContext(schemes=["django_pbkdf2_sha256"], deprecated="auto")




auth_router = APIRouter(
    prefix="/auth", tags=["auth"], responses={422: {"description": "Not Found"}}
)


@auth_router.post('/register/')
async def create_user(user: CreateUserRequest, db: Session = Depends(get_db)):
    """Api to create new user

    Args:\n
        first_name: str (max_length=50)\n
        last_name: str (max_length=50)\n
        organisation_name: str (max_length=50)\n
        email: str (max_length=50)\n
        password: str (min_length=8, max_length=16)\n
        confirm_password: str (min_length=8, max_length=16)\n

    Raises:\n
        HTTPException: Your account has already been registered. Kindly login\n
        HTTPException: Failed to send mail\n
        HTTPException: Failed to crete new user\n
        HTTPException: ValueError\n
        HTTPException: IntegrityError\n 

    Returns:\n
        str : Success message and user_id\n
    """
    try:
        hashed_password = pwd_context.hash(user.password)

        # Check if email already exists
        existing_user = db.query(AuthProfile).filter(AuthProfile.email == user.email).first()
        if existing_user:
            app_logger.info(f"User Creation Failed | {user.email} | User already present")
            raise HTTPException(status_code=400, detail={"flag":0 ,"message":"Your account has already been registered. Kindly login."})
        # Create new user
        # slug = await create_unique_slug()0
        resp, message = await create_new_user(db=db, user=user, hashed_password=hashed_password)
        if resp:
            user_full_name = user.first_name + user.last_name
            app_logger.info(f"User Created Successfully | {user.email} | User Created")
            return {'message': 'User created successfully', 'user_id': message}  
        else:
            app_logger.error(f"User Creation Failed | {user.email} | Failed to save user")
            raise HTTPException(status_code=400, detail=message)

    except ValueError as e:
        app_logger.error(f"User Creation Failed | {user.email} | {e}")
        app_logger.trace(traceback.format_exc(e))
        raise HTTPException(status_code=400, detail=str(e.args))

    except IntegrityError as e:
        db.rollback()
        app_logger.error(f"User Creation Failed | {user.email} | {e}")
        app_logger.trace(traceback.format_exc(e))
        raise HTTPException(status_code=400, detail='Could not create user')
    
    
@auth_router.post('/login/')
async def login(login_user: UserLoginRequest, db: Session = Depends(get_db)):
    """This function is used to login into the portal\n

    Args:\n
        email : str (max_length=50)\n
        password: str (min_length=8, max_length=16)\n

    Raises:\n
        HTTPException: Invalid email or password\n
        HTTPException: Invalid Password\n
        HTTPException: Email not verified\n

    Returns:\n
        JWT token:\n 
    """
    # Get user from database
    user = db.query(AuthProfile).filter(AuthProfile.email == login_user.email).first()
    if not user:
        app_logger.error(f"Login Failed | {None} | User does not exists")
        raise HTTPException(status_code=400, detail={"flag":1 ,"message":"Email Id is not registered"})
    
    # Verify password
    
    if not pwd_context.verify(login_user.password, user.password):
        app_logger.error(f"Login Failed | {user.auth_profile_id} | Invalid Password")
        raise HTTPException(status_code=400, detail={"flag":2 ,"message":'Invalid password'})

    user.last_login = datetime.utcnow()
    user_data = {
        "auth_profile_id":user.auth_profile_id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name" : user.last_name
        }
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token_payload = {'sub': user.email, 'exp': datetime.utcnow() + access_token_expires}
    access_token = jwt.encode(access_token_payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    # Create refresh token
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token_payload = {'sub': user.email + "refresh", 'exp': datetime.utcnow() + refresh_token_expires}
    refresh_token = jwt.encode(refresh_token_payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    app_logger.info(f"Login Successful | {user.auth_profile_id} | None")
    # db.commit()
    db.close()
    return {'access_token': access_token, 'token_type': 'bearer', 'refresh_token': refresh_token, "user_details": user_data}



@auth_router.post('/refresh_token/')
async def refresh(refresh_token: HashSlugRequest, db : Session = Depends(get_db)):
    """A Function to verify the\n 

    Args:\n
        refresh_token (str): str\n

    Raises:\n
        HTTPException: _description_\n
        HTTPException: _description_\n
        HTTPException: _description_\n

    Returns:\n
        _type_: _description_\n
    """
    # Verify refresh token
    try:
        refresh_token_payload = jwt.decode(refresh_token.hash_slug, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
        email = refresh_token_payload.get('sub')
    except JWTError:
        raise HTTPException(status_code=400, detail='Invalid refresh token')

    # Get user from database
    email = email.replace("refresh",'')
    user = db.query(AuthProfile).filter(AuthProfile.email == email).first()
    if not user:
        raise HTTPException(status_code=400, detail='User not found')

    # Create new access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token_payload = {'sub': user.email, 'exp': datetime.utcnow() + access_token_expires}
    access_token = jwt.encode(access_token_payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return {'access_token': access_token, 'token_type': 'bearer'}






