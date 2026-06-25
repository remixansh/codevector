"""Product listing endpoints with cursor-based pagination."""

from typing import Optional

from fastapi import APIRouter, Query

from app.db import get_supabase
from app.schemas import CategoriesResponse, Cursor, Product, ProductsResponse

router = APIRouter(prefix="/api", tags=["products"])


@router.get("/products", response_model=ProductsResponse)
def list_products(
    cursor_created_at: Optional[str] = Query(
        None, description="ISO 8601 timestamp from the previous page's next_cursor"
    ),
    cursor_id: Optional[str] = Query(
        None, description="UUID from the previous page's next_cursor"
    ),
    category: Optional[str] = Query(None, description="Filter by product category"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
):
    """
    Paginated product listing — newest first.

    **First page:** call without cursor params.
    **Next page:** pass `next_cursor.created_at` and `next_cursor.id` from the response.

    Uses keyset (cursor-based) pagination so results stay stable even when
    new products are inserted while the user is browsing.
    """
    client = get_supabase()

    # Request limit + 1 rows to detect whether a next page exists,
    # without needing an expensive COUNT(*) query.
    params = {
        "p_cursor_created_at": cursor_created_at,
        "p_cursor_id": cursor_id,
        "p_category": category,
        "p_limit": limit + 1,
    }

    response = client.rpc("get_products_page", params).execute()
    rows = response.data

    # Determine if there are more results beyond this page.
    has_next = len(rows) > limit
    if has_next:
        rows = rows[:limit]

    # Build the cursor for the next page from the last returned row.
    next_cursor = None
    if has_next and rows:
        last = rows[-1]
        next_cursor = Cursor(created_at=last["created_at"], id=last["id"])

    return ProductsResponse(
        data=[Product(**row) for row in rows],
        next_cursor=next_cursor,
        has_next=has_next,
    )


@router.get("/categories", response_model=CategoriesResponse)
def list_categories():
    """Return all distinct product categories for the filter dropdown."""
    client = get_supabase()
    response = client.rpc("get_categories").execute()
    categories = [row["category"] for row in response.data]
    return CategoriesResponse(data=categories)
