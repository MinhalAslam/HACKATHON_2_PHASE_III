from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
from typing import Optional
from datetime import timedelta
from ..database.database import get_session
from ..models.user import User, UserCreate, UserLogin, UserRead
from ..utils.jwt import create_access_token
from ..utils.auth import get_current_user
import bcrypt
import uuid

router = APIRouter()

security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a hashed password."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


def get_password_hash(password: str) -> str:
    """Hash a plaintext password."""
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


@router.post("/register", response_model=UserRead)
def register_user(user_data: UserCreate, session: Session = Depends(get_session)):
    """Register a new user."""
    # Check if user already exists
    statement = select(User).where(User.email == user_data.email)
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash the password
    hashed_password = get_password_hash(user_data.password)

    # Create new user
    db_user = User(
        email=user_data.email,
        hashed_password=hashed_password
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@router.post("/login")
def login_user(user_data: UserLogin, session: Session = Depends(get_session)):
    """Login a user and return access token."""
    # Find user by email
    statement = select(User).where(User.email == user_data.email)
    user = session.exec(statement).first()

    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=30)  # Use from env in real app
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserRead)
def read_users_me(current_user: User = Depends(get_current_user)):
    """Return the current authenticated user's information."""
    return current_user


@router.post("/logout")
def logout_user():
    """
    Logout endpoint for frontend compatibility.
    Since JWT is stateless, actual logout happens client-side.
    This endpoint exists for API completeness.
    """
    return {"message": "Logged out successfully"}