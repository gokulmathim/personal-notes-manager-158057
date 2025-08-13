from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from src.dependencies import get_db, get_current_user
from src.models.note import Note
from src.models.user import User
from src.schemas.note import NoteCreate, NoteRead, NoteUpdate

router = APIRouter(prefix="/notes", tags=["Notes"])


# PUBLIC_INTERFACE
@router.post(
    "",
    response_model=NoteRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a note",
    description="Create a new note belonging to the authenticated user.",
    responses={201: {"description": "Note created."}, 400: {"description": "Invalid input."}, 401: {"description": "Unauthorized."}},
)
def create_note(payload: NoteCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> NoteRead:
    """Create a new note for the current user."""
    note = Note(title=payload.title, content=payload.content, tags=payload.tags, owner_id=current_user.id)
    db.add(note)
    db.commit()
    db.refresh(note)
    return NoteRead.model_validate(note)


# PUBLIC_INTERFACE
@router.get(
    "",
    response_model=List[NoteRead],
    summary="List notes",
    description="List notes for the authenticated user. Supports simple search and pagination.",
)
def list_notes(
    q: Optional[str] = Query(default=None, description="Search query for title, content, or tags."),
    skip: int = Query(default=0, ge=0, description="Number of records to skip."),
    limit: int = Query(default=50, ge=1, le=100, description="Maximum number of records to return."),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[NoteRead]:
    """List notes with optional search query and pagination."""
    query = db.query(Note).filter(Note.owner_id == current_user.id)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Note.title.ilike(like), Note.content.ilike(like), Note.tags.ilike(like)))
    notes = query.order_by(Note.updated_at.desc()).offset(skip).limit(limit).all()
    return [NoteRead.model_validate(n) for n in notes]


# PUBLIC_INTERFACE
@router.get(
    "/search",
    response_model=List[NoteRead],
    summary="Search notes",
    description="Search notes by query text across title, content, and tags.",
)
def search_notes(
    query: str = Query(..., min_length=1, description="Text to search for."),
    skip: int = Query(default=0, ge=0, description="Number of records to skip."),
    limit: int = Query(default=50, ge=1, le=100, description="Maximum number of records to return."),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[NoteRead]:
    """Search notes owned by the current user."""
    like = f"%{query}%"
    notes = (
        db.query(Note)
        .filter(Note.owner_id == current_user.id)
        .filter(or_(Note.title.ilike(like), Note.content.ilike(like), Note.tags.ilike(like)))
        .order_by(Note.updated_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [NoteRead.model_validate(n) for n in notes]


# PUBLIC_INTERFACE
@router.get(
    "/{note_id}",
    response_model=NoteRead,
    summary="Get a note",
    description="Get a single note by ID, ensuring it belongs to the current user.",
    responses={404: {"description": "Note not found."}},
)
def get_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NoteRead:
    """Retrieve a specific note by ID for the current user."""
    note = db.query(Note).filter(Note.id == note_id, Note.owner_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found.")
    return NoteRead.model_validate(note)


# PUBLIC_INTERFACE
@router.put(
    "/{note_id}",
    response_model=NoteRead,
    summary="Update a note",
    description="Update title, content, and/or tags of a note owned by the current user.",
    responses={404: {"description": "Note not found."}},
)
def update_note(
    note_id: int,
    payload: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NoteRead:
    """Update a note's fields."""
    note = db.query(Note).filter(Note.id == note_id, Note.owner_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found.")

    if payload.title is not None:
        note.title = payload.title
    if payload.content is not None:
        note.content = payload.content
    if payload.tags is not None:
        note.tags = payload.tags

    db.add(note)
    db.commit()
    db.refresh(note)
    return NoteRead.model_validate(note)


# PUBLIC_INTERFACE
@router.delete(
    "/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a note",
    description="Delete a note owned by the current user.",
    responses={204: {"description": "Note deleted."}, 404: {"description": "Note not found."}},
)
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a note."""
    note = db.query(Note).filter(Note.id == note_id, Note.owner_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found.")
    db.delete(note)
    db.commit()
    return None
