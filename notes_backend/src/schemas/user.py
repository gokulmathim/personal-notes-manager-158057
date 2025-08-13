from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base schema for user data."""
    email: EmailStr = Field(..., description="User email.")
    name: Optional[str] = Field(default=None, description="Optional display name.")


class UserCreate(UserBase):
    """Schema for user creation."""
    password: str = Field(..., min_length=6, description="Plaintext password to set for the user.")


class UserRead(UserBase):
    """Schema to return user info."""
    id: int = Field(..., description="Unique user ID.")

    class Config:
        from_attributes = True
