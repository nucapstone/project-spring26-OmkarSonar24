import duckdb
import sys
con = duckdb.connect("../data/capstone.duckdb", read_only=True)

df = con.execute("""
    SELECT 
        t.Merchant_Name as merchant,
        COUNT(*) as transaction_count,
        ROUND(SUM(t.Amount_Completed), 2) as total_spend,
        COUNT(DISTINCT t.CustomerID) as unique_customers
    FROM silver.transactions t
    JOIN gold.mrt_customer_clusters c ON t.CustomerID = c.customer_id
    WHERE t.Amount_Completed > 0
        AND t.Transaction_Date BETWEEN '2025-11-20' AND '2026-01-24'
    GROUP BY 1
    ORDER BY total_spend DESC
    LIMIT 20
""").fetchdf()

df.to_csv(sys.stdout, index=False)
con.close()