from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from src.api.routers import auth as auth_router
from src.api.routers import notes as notes_router
from src.core.config import get_settings
from src.db.session import Base, engine

settings = get_settings()

openapi_tags: List[dict] = [
    {
        "name": "Health",
        "description": "Service health and status endpoints.",
    },
    {
        "name": "Auth",
        "description": "User registration and authentication endpoints.",
    },
    {
        "name": "Notes",
        "description": "CRUD operations and search for notes.",
    },
]

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    openapi_tags=openapi_tags,
)

# CORS
allow_origins = [o.strip() for o in settings.CORS_ALLOW_ORIGINS.split(",")] if settings.CORS_ALLOW_ORIGINS else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# PUBLIC_INTERFACE
@app.get("/", tags=["Health"], summary="Health Check")
def health_check():
    """Simple health check endpoint.

    Returns:
        JSON payload indicating service status.
    """
    return {"message": "Healthy"}


# Include routers
app.include_router(auth_router.router)
app.include_router(notes_router.router)


# Create tables on startup
@app.on_event("startup")
def on_startup():
    """Initialize database schema on service startup."""
    Base.metadata.create_all(bind=engine)


# Customize OpenAPI generation to ensure tags and metadata are present
def custom_openapi():
    """Generate a custom OpenAPI schema with additional metadata."""
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=settings.APP_DESCRIPTION,
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
