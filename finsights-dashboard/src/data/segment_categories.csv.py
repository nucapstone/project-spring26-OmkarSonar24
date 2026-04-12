import duckdb
import pandas as pd
import sys

con = duckdb.connect("../data/capstone.duckdb", read_only=True)
df = con.execute("""
    SELECT
        mcc.cluster_name,
        ROUND(AVG(f.grocery_share) * 100, 1) AS grocery,
        ROUND(AVG(f.dining_share) * 100, 1) AS dining,
        ROUND(AVG(f.gas_share) * 100, 1) AS gas,
        ROUND(AVG(f.digital_share) * 100, 1) AS digital,
        ROUND(AVG(f.retail_share) * 100, 1) AS retail,
        ROUND(AVG(f.healthcare_share) * 100, 1) AS healthcare,
        ROUND(AVG(f.entertainment_share) * 100, 1) AS entertainment,
        ROUND(AVG(f.financial_share) * 100, 1) AS financial,
        ROUND(AVG(f.telecom_share) * 100, 1) AS telecom,
        ROUND(AVG(f.utilities_share) * 100, 1) AS utilities,
        ROUND(AVG(f.other_share) * 100, 1) AS other
    FROM gold.mrt_customer_clusters mcc
    JOIN gold.mrt_customer_features f
        ON mcc.customer_id = f.customer_id
    GROUP BY mcc.cluster_name
""").fetchdf()
con.close()
df.to_csv(sys.stdout, index=False)