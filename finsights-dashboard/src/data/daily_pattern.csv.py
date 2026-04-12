import duckdb
import sys
con = duckdb.connect("../data/capstone.duckdb", read_only=True)

df = con.execute("""
    SELECT
        DAYOFWEEK(t.Transaction_Date) as day_num,
        CASE DAYOFWEEK(t.Transaction_Date)
            WHEN 0 THEN 'Sunday'
            WHEN 1 THEN 'Monday'
            WHEN 2 THEN 'Tuesday'
            WHEN 3 THEN 'Wednesday'
            WHEN 4 THEN 'Thursday'
            WHEN 5 THEN 'Friday'
            WHEN 6 THEN 'Saturday' 
        END as day_name,
        COUNT(*) as transaction_count,
        ROUND(AVG(t.Amount_Completed), 2) as avg_amount,
        ROUND(SUM(t.Amount_Completed), 2) as total_spend           
    FROM silver.transactions t
    JOIN gold.mrt_customer_clusters c ON t.CustomerID = c.customer_id
    WHERE t.Amount_Completed > 0
        AND t.Transaction_Date BETWEEN '2025-11-20' AND '2026-01-24'
    GROUP BY 1, 2
    ORDER BY 1
""").fetchdf()

df.to_csv(sys.stdout, index=False)
con.close()