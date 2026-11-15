import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from app.core.config import settings
from app.core.database import engine, Base
from app.seed import seed_database
from app.api.auth import router as auth_router
from app.api.brand import router as brand_router
from app.api.scanner import router as scanner_router
from app.api.visual import router as visual_router
from app.api.rewrite import router as rewrite_router
from app.api.review import router as review_router
from app.api.analytics import router as analytics_router
from app.api.clarity import router as clarity_router
from app.api.memory import router as memory_router

# Initialize database schema
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Intelligent Brand Governance & Content Intelligence Platform. Tagline: Every Message Matters. Every Brand Deserves Consistency."
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static and uploads folders
app.mount("/static", StaticFiles(directory=settings.STATIC_PATH), name="static")
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_PATH), name="uploads")

# Include API Routers
app.include_router(auth_router, prefix="/api")
app.include_router(brand_router, prefix="/api")
app.include_router(scanner_router, prefix="/api")
app.include_router(visual_router, prefix="/api")
app.include_router(rewrite_router, prefix="/api")
app.include_router(review_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")
app.include_router(clarity_router, prefix="/api")
app.include_router(memory_router, prefix="/api")

@app.on_event("startup")
def on_startup():
    # Seed database with sample brand assets, guidelines, facts, and submissions
    try:
        seed_database()
    except Exception as e:
        print(f"Startup seed notice: {e}")

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "tagline": settings.TAGLINE
    }

# SPA Index Route
INDEX_PATH = os.path.join(settings.STATIC_PATH, "index.html")

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    if os.path.exists(INDEX_PATH):
        return FileResponse(INDEX_PATH)
    return HTMLResponse("<h1>BRANDGUARD AI</h1><p>Platform initializing...</p>")

@app.get("/{full_path:path}", response_class=HTMLResponse)
async def catch_all(full_path: str):
    # If API or static/uploads, return 404 naturally; otherwise fallback to SPA index
    if full_path.startswith(("api/", "static/", "uploads/", "docs", "redoc", "openapi.json")):
        return HTMLResponse("Not Found", status_code=404)
    if os.path.exists(INDEX_PATH):
        return FileResponse(INDEX_PATH)
    return HTMLResponse("<h1>BRANDGUARD AI</h1>")
