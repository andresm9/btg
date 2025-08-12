from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.config import logging
from app.models import UserCreate
from app.database import db
from app.auth import authenticate_user, create_access_token, get_password_hash

router = APIRouter(prefix="/auth")
logger = logging.getLogger(__name__)

@router.post('/login', summary="Endpoint for User Login. Should provide email and password")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Endpoint for User Login. Should provide email and password"""

    logger.info(f"Login attempt for user: {form_data.username}")
    user = await authenticate_user(form_data.username, form_data.password)
    
    if not user:
        logger.error(f"Login failed for user: {form_data.username}")
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": user.email})
    logger.info(f"Login successful for user: {form_data.username}")
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post('/register', status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate):
    """Creates a new User (Customer or Admin)"""
    
    logger.info(f"Registering user: {user.email}")
    
    if await db['User'].find_one({"email": user.email}):
        logger.error(f"Registration failed: email already exists {user.email}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

    hashed_password = get_password_hash(user.password)
    
    user_dict = user.model_dump()
    user_dict.pop("password")
    user_dict["hashed_password"] = hashed_password
    
    if(["Admin"] == user.roles):
        logger.info(f"Registering user with admin role: {user.email}")
        user_dict["balance"] = 0

    await db['User'].insert_one(user_dict)
    
    logger.info(f"User registered successfully: {user.email}")
    return {"message": "User registered successfully"}
