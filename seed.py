"""
Seed script — generates and inserts 200,000 products into Supabase.

Usage:
    python seed.py

Requires SUPABASE_URL and SUPABASE_KEY in .env (use the service role key for writes).
"""

import os
import random
import time
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

TOTAL_PRODUCTS = 200_000
BATCH_SIZE = 1_000  # Supabase REST caps at ~1000 rows per insert

CATEGORIES = [
    "Electronics",
    "Clothing",
    "Home & Garden",
    "Sports",
    "Books",
    "Toys",
    "Food & Beverages",
    "Beauty",
    "Automotive",
    "Office Supplies",
]

ADJECTIVES = [
    "Premium", "Essential", "Classic", "Modern", "Ultra",
    "Pro", "Elite", "Basic", "Deluxe", "Compact",
]

NOUNS = [
    "Widget", "Gadget", "Device", "Kit", "Set",
    "Tool", "Pack", "Bundle", "System", "Gear",
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def random_product_name(index: int) -> str:
    """Generate a human-readable product name."""
    adj = random.choice(ADJECTIVES)
    noun = random.choice(NOUNS)
    return f"{adj} {noun} {index + 1}"


def random_timestamp() -> str:
    """Return an ISO 8601 timestamp spread across the past year."""
    now = datetime.now(timezone.utc)
    offset = timedelta(
        days=random.randint(0, 365),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59),
    )
    return (now - offset).isoformat()


def generate_batch(batch_num: int) -> list[dict]:
    """Create BATCH_SIZE product dicts ready for insertion."""
    products = []
    base_index = batch_num * BATCH_SIZE

    for i in range(BATCH_SIZE):
        ts = random_timestamp()
        products.append({
            "name": random_product_name(base_index + i),
            "category": random.choice(CATEGORIES),
            "price": round(random.uniform(1.00, 999.99), 2),
            "created_at": ts,
            "updated_at": ts,
        })

    return products


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def seed():
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    total_batches = TOTAL_PRODUCTS // BATCH_SIZE

    print(f"Seeding {TOTAL_PRODUCTS:,} products in {total_batches} batches of {BATCH_SIZE}…")
    start = time.time()

    for batch_num in range(total_batches):
        batch = generate_batch(batch_num)
        client.table("products").insert(batch).execute()

        elapsed = time.time() - start
        pct = (batch_num + 1) / total_batches * 100
        print(f"  [{batch_num + 1}/{total_batches}] {pct:.0f}% — {elapsed:.1f}s elapsed")

    elapsed = time.time() - start
    print(f"\nDone! Inserted {TOTAL_PRODUCTS:,} products in {elapsed:.1f}s.")


if __name__ == "__main__":
    seed()
