import duckdb
import sys
con = duckdb.connect("../data/capstone.duckdb", read_only=True)

df = con.execute("""
    SELECT 
        MONTHNAME(t.Transaction_Date) as month,
        MONTH(t.Transaction_Date) as month_num,
        COUNT(*) as transaction_count,
        COUNT(DISTINCT t.CustomerID) as active_customers,
        ROUND(AVG(t.Amount_Completed), 2) as avg_amount,
        ROUND(SUM(t.Amount_Completed), 2) as total_spend
    FROM silver.transactions t
    JOIN gold.mrt_customer_clusters c ON t.CustomerID = c.customer_id
    WHERE t.Amount_Completed > 0
        AND t.Transaction_Date BETWEEN '2025-11-20' AND '2026-01-24'
    GROUP BY 1, 2
    ORDER BY 2
""").fetchdf()

df.to_csv(sys.stdout, index=False)
con.close()