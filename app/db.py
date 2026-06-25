"""Supabase client singleton."""

from supabase import Client, create_client

from app.config import SUPABASE_KEY, SUPABASE_URL

_client: Client | None = None


def get_supabase() -> Client:
    """Return a reusable Supabase client instance."""
    global _client
    if _client is None:
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _client
