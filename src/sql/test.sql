 */
        SELECT 
    -- selects constants 1 and 2, aliasing them as "one" and "two" respectively
    1 AS one,
    2 AS two
FROM dbo.test 
-- limits the number of returned rows to 100
LIMIT 100;