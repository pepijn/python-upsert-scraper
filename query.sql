--*- fill-column: 66; -*-

CREATE TABLE IF NOT EXISTS scraps (
    id serial PRIMARY KEY,
    hash bytea NOT NULL UNIQUE,
    body text NOT NULL,
    seen_at timestamptz[] NOT NULL
);

-- This extension yields the digest function that enables us to
-- hash the body and index it efficiently. Moreover, PostgreSQL
-- does not allow indexes on very large text columns. We expect to
-- store large HTML bodies so we definitely need the hashing.
CREATE EXTENSION IF NOT EXISTS pgcrypto;


-- Capture the script input (body) via a CTE (the WITH part) so we
-- can use it multiple times in the query. Once to save the body,
-- once to hash it.
WITH body AS (SELECT :body::text AS txt)

-- This is exactly the INSERT you would write without UPSERT.
INSERT INTO scraps (hash, body, seen_at)
    SELECT digest(txt, 'sha1'), txt, ARRAY[:ts::timestamptz]
    FROM body

-- Here it gets interesting; we utilize the UNIQUE index on hash
-- to yield a conflict if the body already exists. If that
-- happens, we append the new seen_at (via the special 'EXCLUDED'
-- table) to the seen_at array.
  ON CONFLICT (hash) DO UPDATE
    SET seen_at = scraps.seen_at || EXCLUDED.seen_at

-- The query returns a summary of the row so I can use it in my
-- blog post. This part will run, but the output is ignored, in
-- production.
RETURNING id, left(hash::text, 3) || '...' hash, body, seen_at;
