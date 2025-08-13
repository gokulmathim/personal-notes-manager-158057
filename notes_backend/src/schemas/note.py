from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class NoteBase(BaseModel):
    """Base schema for notes."""
    title: str = Field(..., min_length=1, description="Title of the note.")
    content: str = Field(..., description="Content/body of the note.")
    tags: Optional[str] = Field(default=None, description="Optional comma-separated tags.")


class NoteCreate(NoteBase):
    """Schema for creating a note."""
    pass


class NoteUpdate(BaseModel):
    """Schema for updating an existing note."""
    title: Optional[str] = Field(default=None, description="New title of the note.")
    content: Optional[str] = Field(default=None, description="New content/body of the note.")
    tags: Optional[str] = Field(default=None, description="New comma-separated tags.")


class NoteRead(NoteBase):
    """Schema for returning a note."""
    id: int = Field(..., description="Unique note ID.")
    owner_id: int = Field(..., description="Owner user ID.")
    created_at: datetime = Field(..., description="Creation timestamp.")
    updated_at: datetime = Field(..., description="Last update timestamp.")

    class Config:
        from_attributes = True
