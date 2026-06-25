-- =============================================
-- CodeVector Product Browser — RPC Functions
-- =============================================

-- Cursor-based paginated product listing.
-- Uses row-value comparison (created_at, id) < (cursor) for keyset pagination.
-- This is stable under concurrent inserts — no duplicates, no skipped rows.
CREATE OR REPLACE FUNCTION get_products_page(
    p_cursor_created_at TIMESTAMPTZ DEFAULT NULL,
    p_cursor_id         UUID        DEFAULT NULL,
    p_category          TEXT        DEFAULT NULL,
    p_limit             INT         DEFAULT 20
)
RETURNS SETOF products
LANGUAGE sql
STABLE
AS $$
    SELECT *
    FROM products
    WHERE
        (p_category IS NULL OR category = p_category)
        AND (
            p_cursor_created_at IS NULL
            OR (created_at, id) < (p_cursor_created_at, p_cursor_id)
        )
    ORDER BY created_at DESC, id DESC
    LIMIT p_limit;
$$;


-- Distinct category list for filter dropdowns.
CREATE OR REPLACE FUNCTION get_categories()
RETURNS TABLE(category TEXT)
LANGUAGE sql
STABLE
AS $$
    SELECT DISTINCT category FROM products ORDER BY category;
$$;
