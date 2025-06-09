SELECT
    1 AS one, -- Hardcoded value 1 aliased as 'one'
    2 AS two -- Hardcoded value 2 aliased as 'two'
FROM dbo.test
LIMIT 100; -- Restricts output to first 100 rows