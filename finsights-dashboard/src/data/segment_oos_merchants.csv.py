import duckdb
import pandas as pd
import sys

con = duckdb.connect("../data/capstone.duckdb", read_only=True)
df = con.execute("""
    SELECT
        mcc.cluster_name,
        t.Merchant_Name,
        COUNT(*) AS txn_count,
        ROUND(SUM(t.Amount_Completed), 2) AS total_spend,
        COUNT(DISTINCT t.CustomerID) AS unique_customers
    FROM gold.mrt_customer_clusters mcc
    JOIN silver.transactions t
        ON mcc.customer_id = t.CustomerID
    WHERE RIGHT(t.ATM_City_State, 2) != 'ME'
        AND t.ATM_City_State IS NOT NULL
        AND t.Amount_Completed > 0
        AND t.Transaction_Date BETWEEN '2025-11-20' AND '2026-01-24'
    GROUP BY mcc.cluster_name, t.Merchant_Name
    ORDER BY mcc.cluster_name, total_spend DESC
""").fetchdf()
con.close()

df = df.groupby("cluster_name").head(10)
df.to_csv(sys.stdout, index=False)