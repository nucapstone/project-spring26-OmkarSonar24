import duckdb
import pandas as pd
import sys
con = duckdb.connect("../data/capstone.duckdb", read_only=True)

df = con.execute("""
    SELECT
        mcc.cluster_name,
        CASE
            WHEN t.Recurring_Trxn = 'Y' THEN 'Recurring'
            ELSE 'Non-Recurring'
        END AS txn_type,
        COUNT(*) AS txn_count,
        ROUND(SUM(t.Amount_Completed), 2) AS total_spend,
        ROUND(AVG(t.Amount_Completed), 2) AS avg_amount
    FROM gold.mrt_customer_clusters mcc
    JOIN silver.transactions t
        ON mcc.customer_id = t.CustomerID
    WHERE t.Amount_Completed > 0
        AND t.Transaction_Date BETWEEN '2025-11-20' AND '2026-01-24'
    GROUP BY mcc.cluster_name, txn_type
    ORDER BY mcc.cluster_name, txn_type
""").fetchdf()

con.close()
df.to_csv(sys.stdout, index=False)