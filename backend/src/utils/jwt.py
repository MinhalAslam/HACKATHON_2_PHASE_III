from datetime import datetime, timedelta
from typing import Optional
import jwt
from sqlmodel import Session
from fastapi import HTTPException, status
from ..models.user import User
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-default-secret-key-change-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Creates a JWT access token with the given data and expiration time.

    Args:
        data: Dictionary containing the data to encode in the token
        expires_delta: Optional timedelta for custom expiration, defaults to ACCESS_TOKEN_EXPIRE_MINUTES

    Returns:
        Encoded JWT token as string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str, credentials_exception):
    """
    Verifies a JWT token and returns the user ID if valid.

    Args:
        token: JWT token to verify
        credentials_exception: HTTPException to raise if token is invalid

    Returns:
        User ID from the token payload
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        # Additional validation: check if user exists in DB could be added here
        # For now, we just return the user ID from the token

        return user_id

    except jwt.ExpiredSignatureError:
        raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception


def get_current_user_from_token(token: str):
    """
    Gets the current user from a JWT token.

    Args:
        token: JWT token to decode

    Returns:
        User ID from the token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user_id = verify_token(token, credentials_exception)
    return user_id