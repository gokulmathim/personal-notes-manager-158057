from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.core.security import get_password_hash, verify_password, create_access_token
from src.dependencies import get_db, get_current_user
from src.models.user import User
from src.schemas.auth import Token, RegisterRequest
from src.schemas.user import UserRead

router = APIRouter(prefix="/auth", tags=["Auth"])


# PUBLIC_INTERFACE
@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email and password.",
    responses={
        201: {"description": "User successfully registered."},
        400: {"description": "Invalid input or user already exists."},
    },
)
def register_user(payload: RegisterRequest, db: Session = Depends(get_db)) -> UserRead:
    """Create a new user with a hashed password and return the public user info."""
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered.")

    user = User(email=payload.email, name=payload.name, hashed_password=get_password_hash(payload.password))
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered.")
    return UserRead.model_validate(user)


# PUBLIC_INTERFACE
@router.post(
    "/login",
    response_model=Token,
    summary="Login and get access token",
    description="Authenticate using email and password (OAuth2 Password flow) and receive a JWT token.",
    responses={
        200: {"description": "Authentication successful."},
        400: {"description": "Missing credentials."},
        401: {"description": "Invalid email or password."},
    },
)
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)
) -> Token:
    """Validate user credentials and return a JWT access token."""
    email = form_data.username
    password = form_data.password
    if not email or not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email and password are required.")

    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password.")

    token = create_access_token(subject=user.email)
    return Token(access_token=token, token_type="bearer")


# PUBLIC_INTERFACE
@router.get(
    "/me",
    response_model=UserRead,
    summary="Get current user profile",
    description="Return the profile of the authenticated user.",
    responses={200: {"description": "Current user information."}, 401: {"description": "Unauthorized."}},
)
def read_users_me(current_user: User = Depends(get_current_user)) -> UserRead:
    """Return the profile information for the current authenticated user."""
    return UserRead.model_validate(current_user)
