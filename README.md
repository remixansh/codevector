# CodeVector Product Browser

A backend that lets someone browse ~200,000 products (newest first), filter by category, and paginate through them — with **stable pagination** even while data is changing.

## Tech Stack

- **Backend:** Python / FastAPI
- **Database:** Supabase (PostgreSQL)
- **Pagination:** Cursor-based (keyset) using `(created_at, id)` composite cursor
- **Frontend:** Vanilla HTML/CSS/JS (bonus)

## Why Cursor-Based Pagination?

The spec requires that if 50 new products are added while someone is browsing, they must not see duplicates or miss any products.

**Offset-based pagination fails here** — inserting rows shifts offsets and causes duplicates/skips.

**Cursor-based pagination** filters by values (`WHERE (created_at, id) < (cursor_created_at, cursor_id)`), so new inserts above the cursor don't affect already-paginated results. This gives O(log n) performance regardless of page depth, and perfect stability under concurrent writes.

### How the cursor works

1. Products are ordered by `created_at DESC, id DESC`
2. After each page, the API returns a `next_cursor` containing the last row's `(created_at, id)`
3. The next request passes this cursor, and the RPC function uses `(created_at, id) < (cursor)` to efficiently seek to the next set
4. PostgreSQL's row-value comparison maps directly to our composite index

## Setup

```bash
# 1. Clone the repo
git clone <repo-url>
cd codevector

# 2. Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate   # Windows
source venv/bin/activate  # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your Supabase URL and key

# 5. Set up the database
# Run sql/schema.sql in Supabase SQL Editor (creates table + indexes)
# Run sql/functions.sql in Supabase SQL Editor (creates RPC functions)

# 6. Seed the database (200,000 products)
python seed.py

# 7. Start the server
uvicorn app.main:app --reload
```

Open http://localhost:8000 for the UI, or http://localhost:8000/docs for the API docs.

## API Endpoints

### `GET /api/products`

| Parameter | Type | Default | Description |
|---|---|---|---|
| `limit` | int (1-100) | 20 | Items per page |
| `category` | string | — | Filter by category |
| `cursor_created_at` | ISO 8601 | — | Cursor timestamp from `next_cursor` |
| `cursor_id` | UUID | — | Cursor ID from `next_cursor` |

**Response:**
```json
{
  "data": [{ "id": "...", "name": "...", "category": "...", "price": 29.99, "created_at": "...", "updated_at": "..." }],
  "next_cursor": { "created_at": "...", "id": "..." },
  "has_next": true
}
```

### `GET /api/categories`

Returns all distinct product categories.

## What I'd Improve With More Time

- **Search** — full-text search on product name
- **Sorting options** — sort by price, name, etc.
- **Rate limiting** — protect the API from abuse
- **Caching** — Redis layer for hot queries
- **Tests** — pytest suite with mocked Supabase client
- **Docker** — containerized deployment
- **CI/CD** — GitHub Actions for automated testing and deployment

## Project Structure

```
codevector/
├── sql/
│   ├── schema.sql        # Table, indexes, trigger, RLS
│   └── functions.sql     # RPC functions for pagination
├── app/
│   ├── main.py           # FastAPI app entry point
│   ├── config.py         # Environment settings
│   ├── db.py             # Supabase client singleton
│   ├── schemas.py        # Pydantic response models
│   └── routes/
│       └── products.py   # API endpoints
├── frontend/
│   └── index.html        # Bonus UI
├── seed.py               # Data generation script
├── requirements.txt
├── .env.example
└── README.md
```
