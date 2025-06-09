SELECT
1 AS one,  -- Selecting a constant value of 1 and aliasing it as 'one'
2 AS two   -- Selecting a constant value of 2 and aliasing it as 'two'
FROM dbo.test  -- Specifying the source table 'test' in the 'dbo' schema
LIMIT 100;  -- Limiting the result set to 100 rows