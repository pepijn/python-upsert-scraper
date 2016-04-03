SET timezone TO 'Europe/Amsterdam';

CREATE TABLE IF NOT EXISTS scraps (
  id serial PRIMARY KEY,
  body text NOT NULL UNIQUE,
  seen_at timestamptz[] NOT NULL
);

INSERT INTO scraps (body, seen_at) VALUES (%s, ARRAY[%s::timestamptz])
  ON CONFLICT (body) DO
    UPDATE SET seen_at = scraps.seen_at || EXCLUDED.seen_at;

WITH
  last_observations AS (
    SELECT body, unnest(seen_at) AS seen_at
    FROM scraps
    ORDER BY seen_at DESC
    LIMIT 2),
  distinct_observations AS (
    SELECT DISTINCT ON (body) seen_at, body
    FROM last_observations
  )
SELECT *
FROM distinct_observations
ORDER BY seen_at DESC;
