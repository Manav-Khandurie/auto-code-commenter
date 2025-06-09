SELECT
    1 AS one,  -- Hardcoded value for column 'one'
    2 AS two  -- Hardcoded value for column 'two'
FROM dbo.test  -- Source table
LIMIT 100;  -- Restrict results to first 100 rows