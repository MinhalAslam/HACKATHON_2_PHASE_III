from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from .jwt import verify_token
from sqlmodel import Session
from ..database.database import get_session
from ..models.user import User
import jwt


# HTTPBearer for extracting JWT tokens from Authorization header
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
):
    """
    Dependency to get the current authenticated user from JWT token.

    Args:
        credentials: HTTP authorization credentials containing the JWT token
        session: Database session for user lookup

    Returns:
        User object if token is valid and user exists
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user_id = verify_token(credentials.credentials, credentials_exception)

    # Retrieve user from database
    user = session.get(User, user_id)
    if user is None:
        raise credentials_exception

    return user


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Dependency to get the current authenticated user ID from JWT token.
    This is useful when we just need the user ID without fetching the full user object.

    Args:
        credentials: HTTP authorization credentials containing the JWT token

    Returns:
        User ID string if token is valid
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user_id = verify_token(credentials.credentials, credentials_exception)
    return user_id


def verify_user_owns_resource(user_id: str, resource_user_id: str):
    """
    Verifies that a user owns a specific resource.

    Args:
        user_id: ID of the authenticated user
        resource_user_id: ID of the user that owns the resource

    Raises:
        HTTPException: If user doesn't own the resource
    """
    if user_id != resource_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have permission to access this resource"
        )


def verify_url_user_id_matches_token(url_user_id: str, token_user_id: str):
    """
    Verifies that the user_id in the URL matches the user_id in the JWT token.

    Args:
        url_user_id: User ID from the URL path parameter
        token_user_id: User ID extracted from the JWT token

    Raises:
        HTTPException: If user IDs don't match
    """
    if url_user_id != token_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="URL user_id does not match authenticated user_id"
        )


def handle_auth_error(error: Exception, context: str = "Authentication"):
    """
    Comprehensive error handler for authentication-related failures.

    Args:
        error: The exception that occurred
        context: Context string for logging

    Returns:
        HTTPException with appropriate error message
    """
    import traceback
    print(f"{context} error: {str(error)}")
    print(traceback.format_exc())

    if isinstance(error, jwt.exceptions.ExpiredSignatureError):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    elif isinstance(error, jwt.exceptions.JWTError):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    else:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(error)}",
        )