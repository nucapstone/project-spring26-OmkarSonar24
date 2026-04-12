import duckdb
import sys
con = duckdb.connect("../data/capstone.duckdb", read_only=True)

df = con.execute("""
    SELECT 
        COALESCE(m.category, 'Unknown') as category,
        COUNT(*) as transaction_count,
        ROUND(SUM(t.Amount_Completed), 2) as total_spend,
        ROUND(AVG(t.Amount_Completed), 2) as avg_amount,
        COUNT(DISTINCT t.CustomerID) as unique_customers
    FROM silver.transactions t
    JOIN gold.mrt_customer_clusters c ON t.CustomerID = c.customer_id
    LEFT JOIN gold.mrt_mcc_categories m
        ON t.Merchant_Category = m.Merchant_Category
    WHERE t.Amount_Completed > 0
        AND t.Transaction_Date BETWEEN '2025-11-20' AND '2026-01-24'
    GROUP BY 1
    ORDER BY total_spend DESC
""").fetchdf()

df.to_csv(sys.stdout, index=False)
con.close()