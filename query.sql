CREATE TABLE IF NOT EXISTS scraps (
    id serial PRIMARY KEY,
    hash bytea NOT NULL UNIQUE,
    body text NOT NULL,
    seen_at timestamptz[] NOT NULL
);

CREATE EXTENSION IF NOT EXISTS pgcrypto;

WITH body AS (SELECT %s::text AS txt)
INSERT INTO scraps (hash, body, seen_at)
    SELECT digest(txt, 'sha1'), txt, ARRAY[%s::timestamptz]
    FROM body
  ON CONFLICT (hash) DO UPDATE
    SET seen_at = scraps.seen_at || EXCLUDED.seen_at;

WITH last_observations AS (
       SELECT body, unnest(seen_at) AS seen_at
       FROM scraps
       ORDER BY seen_at DESC
       LIMIT 2),
     distinct_observations AS (
       SELECT DISTINCT ON (body) seen_at, body
       FROM last_observations)
SELECT *
FROM distinct_observations
ORDER BY seen_at DESC;
