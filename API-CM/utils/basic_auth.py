from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials, HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from jose import jwt
from db_module.connection import get_db
from jwt.exceptions import PyJWTError
from sqlalchemy.orm import Session
from utils.config import get_settings
from datetime import datetime, date
from typing import Optional
from models import AuthProfile
from db_module.connection import get_db
 
 
settings = get_settings()
security = HTTPBasic()
pwd_context = CryptContext(schemes=["django_pbkdf2_sha256"], deprecated="auto")
 
 
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
 
async def decodeJWT(token: str) -> Optional[dict]:
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        # return decoded_token if decoded_token.get("exp") >= datetime.now().timestamp() else None
        return {
            "email": decoded_token.get("sub")
        }
    except PyJWTError:
        return None
 
 
class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)
 
    async def __call__(self, request: Request):
        credentials: Optional[HTTPAuthorizationCredentials] = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid authentication scheme.")
            resp = await self.verify_jwt(credentials.credentials)
            if not resp:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token or expired token.")
            return credentials.credentials
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization code.")
 
    async def verify_jwt(self, jwtoken: str) -> bool:
        isTokenValid: bool = False
 
        try:
            payload = await decodeJWT(jwtoken)
        except:
            payload = None
        if payload:
            isTokenValid = True
        return isTokenValid
   
 
jwt_bearer = JWTBearer()
 
# Dependency to get the current user from the token
async def get_current_user(token: str = Depends(jwt_bearer), db: Session = Depends(get_db)) -> dict:
    decoded_token = await decodeJWT(token)
    if decoded_token is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid or expired token.")
    email = decoded_token.get("email")
    user = db.query(AuthProfile).filter(AuthProfile.email == email).first()
 
    if user is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not found.")
   
    return {
        "user_id": user.auth_profile_id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_active": user.is_active
    }