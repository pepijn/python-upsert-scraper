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
