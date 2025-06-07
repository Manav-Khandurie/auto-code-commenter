SELECT
    1 AS one,  -- Static value 1 returned as column 'one'
    2 AS two   -- Static value 2 returned as column 'two'
FROM dbo.test  -- Source table for the query (though columns aren't used)
LIMIT 100;     -- Restrict results to first 100 rows