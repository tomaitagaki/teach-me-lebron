from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from routers import chat, onboarding
from config import get_settings
from logging_config import setup_logging, get_logger
import uvicorn

# Initialize logging
setup_logging(log_level="INFO", log_file=True)
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Teach Me LeBron - Sports Lore Chatbot",
    description="A chatbot that helps you keep up with sports conversations in layman's terms",
    version="1.0.0"
)

logger.info("Application starting up...")

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)
app.include_router(onboarding.router)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    """Serve the main chat interface."""
    return FileResponse("static/index.html")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "teach-me-lebron"}


if __name__ == "__main__":
    settings = get_settings()
    logger.info(f"Starting server on {settings.host}:{settings.port}")
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
