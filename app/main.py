"""FastAPI application entry point."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.routes.products import router as products_router

app = FastAPI(
    title="CodeVector Product Browser",
    description="Browse 200k products with cursor-based pagination",
    version="1.0.0",
)

# Allow the frontend (and any origin during development) to call the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes FIRST — these must take priority.
app.include_router(products_router)

# Resolve the frontend directory relative to this file, so it works
# regardless of the working directory (local dev vs Render vs Docker).
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


@app.get("/", include_in_schema=False)
def serve_frontend():
    """Serve the bonus UI at the root path."""
    return FileResponse(FRONTEND_DIR / "index.html")
