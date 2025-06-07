SELECT
    1 AS one,  -- Hardcoded value 1 aliased as 'one'
    2 AS two   -- Hardcoded value 2 aliased as 'two'
FROM dbo.test -- Source table
LIMIT 100;    -- Limit results to 100 rows