from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
import datetime
from datetime import timedelta
from app.database import db
from app.models import User
from app.config import logging

SECRET_KEY = "NestorAndresMartinez"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """Hash a password for storing in the database"""
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str):
    """Authenticate a user with email and password."""

    logger.info(f"Authenticating user with email: {username}")
    
    user = db.users.find_one({"email": username})

    if not user:
        logger.warning(f"Authentication failed: user not found for email {username}")
        return False
    
    if not verify_password(password, user["hashed_password"]):

        logger.warning(f"Authentication failed: incorrect password for email {username}")
        return False
    
    logger.info(f"Authentication successful for email {username}")
    return User(**user)


def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create a new access token based on the user email."""

    logger.info(f"Creating access token for {data.get('sub')}")
    to_encode = data.copy()

    expire = datetime.datetime.now(datetime.UTC) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.info(f"Access token created for {data.get('sub')}")

    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get the current user from the request."""    

    logger.info("Getting current user from token.")

    # create the Exception object if there is no valid user
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            logger.warning("Token payload missing 'sub'.")
            raise credentials_exception
        
    except JWTError:
        logger.warning("JWTError during token decode.")
        raise credentials_exception
    
    user = db.users.find_one({"email": username})
    
    if user is None:
        logger.warning(f"User not found for email {username}.")
        raise credentials_exception
    
    logger.info(f"Current user: {username}")
    return User(**user)
