from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import settings
from .database import create_tables
from .tasks.api import router as tasks_router
from .auth_api import router as auth_router
from .assistant.api import router as assistant_router
from .assistant.assistant_manager import assistant_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_tables()
    
    # Initialize assistants
    try:
        await assistant_manager.initialize_assistants()
        print("✅ Assistants initialized successfully")
    except Exception as e:
        print(f"⚠️ Warning: Failed to initialize assistants: {e}")
    
    yield
    # Shutdown
    pass


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A comprehensive Task Management API with JWT authentication",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["root"])
def read_root():
    """Root endpoint with API information."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc",
        "legacy_greeting": f"Hello {settings.name}"
    }


@app.get("/health", tags=["health"])
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": settings.app_name}


# Include routers
app.include_router(auth_router)
app.include_router(tasks_router)
app.include_router(assistant_router)
