"""Pydantic response models for the Products API."""

from datetime import datetime

from pydantic import BaseModel


class Product(BaseModel):
    """Single product record."""

    id: str
    name: str
    category: str
    price: float
    created_at: datetime
    updated_at: datetime


class Cursor(BaseModel):
    """Opaque pagination cursor — wraps the last-seen (created_at, id) pair."""

    created_at: str
    id: str


class ProductsResponse(BaseModel):
    """Paginated product listing."""

    data: list[Product]
    next_cursor: Cursor | None = None
    has_next: bool = False


class CategoriesResponse(BaseModel):
    """List of distinct product categories."""

    data: list[str]
