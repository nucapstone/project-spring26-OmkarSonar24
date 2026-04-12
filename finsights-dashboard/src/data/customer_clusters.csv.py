import duckdb
import sys

con = duckdb.connect("../data/capstone.duckdb", read_only=True)

df = con.execute("""
    SELECT 
        f.*,
        c.cluster,
        c.cluster_name
    FROM gold.mrt_customer_features f
    JOIN gold.mrt_customer_clusters c 
        ON f.customer_id = c.customer_id
""").fetchdf()

df.to_csv(sys.stdout, index=False)
con.close()