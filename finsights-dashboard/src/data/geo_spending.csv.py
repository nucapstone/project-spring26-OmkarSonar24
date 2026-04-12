import duckdb
import sys
con = duckdb.connect("../data/capstone.duckdb", read_only=True)

df = con.execute("""
    SELECT 
        TRIM(UPPER(LEFT(t.ATM_City_State, LENGTH(t.ATM_City_State) - 2))) as city,
        RIGHT(t.ATM_City_State, 2) as state,
        COUNT(*) as transaction_count,
        ROUND(SUM(t.Amount_Completed), 2) as total_spend,
        COUNT(DISTINCT t.CustomerID) as unique_customers
    FROM silver.transactions t
    JOIN gold.mrt_customer_clusters c ON t.CustomerID = c.customer_id
    WHERE t.Amount_Completed > 0
        AND t.ATM_City_State IS NOT NULL
        AND LENGTH(t.ATM_City_State) > 2
        AND t.Transaction_Date BETWEEN '2025-11-20' AND '2026-01-24'
    GROUP BY 1, 2
    ORDER BY total_spend DESC
    LIMIT 30
""").fetchdf()

df.to_csv(sys.stdout, index=False)
con.close()