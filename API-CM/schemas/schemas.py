from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
from fastapi import HTTPException
import re
import os
 
# Regular expressions for validation
email_regex = r"^(?![_$&+,:;=?@#|'<>.^*()%!-])(?!.*[_$&+,:;=?@#|'<>.^*()%!-]{2})(?!.*[_$&+,:;=?@#|'<>.^*()%!-]$)[$&+,:;=?#|'<>.^*()%!\w.-]{1,50}@(?:[a-zA-Z0-9.-]{1,50}\.)[a-zA-Z]{2,}$"
password_regex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[_$&+,:;=?@#|'<>.^*()%!-])[A-Za-z\d_$&+,:;=?@#|'<>.^*()%!-]{8,}$"
path_regex = r"^(?![_$&+,:;=?@#|'<>.^*()%!-])(?!.*[_$&+,:;=?@#|'<>.^*()%!-]{2})(?!.*[_$&+,:;=?@#|'<>.^*()%!-]$)[$&+,:;=?#|'<>.^*()%!\w.-/]{1,}$"
 
 
class CreateUserRequest(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=30)
    last_name: str = Field(..., min_length=3, max_length=30)
    email: str
    password: str
    confirm_password: str
 
    class Config:
        orm_mode = True
 
    # Custom error message for first_name field
    @validator('first_name')
    def validate_first_name(cls, first_name):
        if not first_name:
            raise HTTPException(status_code=422, detail='First Name should not be empty')
        if not re.fullmatch(r'^[a-zA-Z]+$', first_name):
            raise HTTPException(status_code=422, detail='First Name should only contain alphabets and spaces')
        return first_name
 
    # Custom error message for last_name field
    @validator('last_name')
    def validate_last_name(cls, last_name):
        if not last_name:
            raise HTTPException(status_code=422, detail='Last Name should not be empty')
        if not re.fullmatch(r'^[a-zA-Z]+$', last_name):
            raise HTTPException(status_code=422, detail='Last Name should only contain alphabets and spaces')
        return last_name
 
    # Custom error message for email field
    @validator('email')
    def validate_email(cls, email):
        if not email:
            raise HTTPException(status_code=422, detail='Email should not be empty')
        if len(email) > 50:
            raise HTTPException(status_code=422, detail='Length of Email should be less than 50 characters')
        if not re.fullmatch(email_regex, email):
            raise HTTPException(status_code=422, detail='Invalid Email Format')
        return email
 
    @validator('password')
    def validate_password(cls, password):
        if not password:
            raise HTTPException(status_code=422, detail='password should not be empty')
        if len(password) < 8 or len(password) > 16:
            raise HTTPException(status_code=422, detail='Length of password should be in 8 to 16 character')
        if not re.fullmatch(password_regex, password):
            raise HTTPException(status_code=422, detail='Invalid password Format')
        return password
 
    # Password confirmation validator
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values.get('password'):
            raise HTTPException(status_code=422, detail='Passwords do not match')
        return v
 
class UserLoginRequest(BaseModel):
    email: str = Field(..., max_length=50)
    password: str = Field(..., min_length=8, max_length=16)
 
    @validator('email')
    def validate_email(cls, email):
        if not email:
            raise HTTPException(status_code=422, detail='Email should not be empty')
        if not re.fullmatch(email_regex, email):
            raise HTTPException(status_code=422, detail='Email should only contain alphabets and spaces')
        return email
 
    @validator('password')
    def validate_password(cls, password):
        if not password:
            raise HTTPException(status_code=422, detail='password should not be empty')
        if not re.fullmatch(password_regex, password):
            raise HTTPException(status_code=422, detail='Invalid password Format')
        return password
 
class HashSlugRequest(BaseModel):
    hash_slug: str
 
    @validator('hash_slug')
    def validate_hash_slug(cls, hash_slug):
        if not hash_slug:
            raise HTTPException(status_code=422, detail='hash slug should not be empty')
        return hash_slug