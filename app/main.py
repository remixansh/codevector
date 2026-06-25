"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

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

# Register API routes.
app.include_router(products_router)

# Serve the bonus frontend at /
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
