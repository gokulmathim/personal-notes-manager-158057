from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt
from passlib.context import CryptContext

from src.core.config import get_settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# PUBLIC_INTERFACE
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify that the provided plain password matches the stored hash."""
    return pwd_context.verify(plain_password, hashed_password)


# PUBLIC_INTERFACE
def get_password_hash(password: str) -> str:
    """Hash the provided plain text password using bcrypt."""
    return pwd_context.hash(password)


# PUBLIC_INTERFACE
def create_access_token(subject: str, expires_delta_minutes: Optional[int] = None) -> str:
    """Create a JWT access token for the given subject (typically the user ID or email).

    Args:
        subject: The subject to encode in the token (e.g., user id or email).
        expires_delta_minutes: Minutes until token expiration. Defaults to settings.

    Returns:
        A signed JWT token string.
    """
    settings = get_settings()
    expire_minutes = expires_delta_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    to_encode = {"sub": subject, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt
