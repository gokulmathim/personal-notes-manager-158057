from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    """JWT access token response payload."""
    access_token: str = Field(..., description="JWT access token.")
    token_type: str = Field(default="bearer", description="Type of token.")


class LoginRequest(BaseModel):
    """Login request payload."""
    email: EmailStr = Field(..., description="User email.")
    password: str = Field(..., description="User password.")


class RegisterRequest(BaseModel):
    """Registration payload."""
    email: EmailStr = Field(..., description="Valid user email.")
    password: str = Field(..., min_length=6, description="Password with minimum length 6 characters.")
    name: Optional[str] = Field(default=None, description="Optional display name.")
