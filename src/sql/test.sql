SELECT
1 AS one,  -- Selecting a constant value of 1 and aliasing it as 'one'
2 AS two   -- Selecting a constant value of 2 and aliasing it as 'two'
FROM dbo.test  -- Querying from the test table in dbo schema
LIMIT 100;  -- Restricting results to first 100 rows