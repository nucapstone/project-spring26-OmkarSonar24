import duckdb
import sys
con = duckdb.connect("../data/capstone.duckdb", read_only=True)

df = con.execute("""
    SELECT
        c.Gender AS gender,
        f.Age AS age
    FROM gold.mrt_customer_features f
    JOIN gold.mrt_customer_clusters cl ON f.customer_id = cl.customer_id
    JOIN silver.customers c ON f.customer_id = c.CustomerID
""").fetchdf()

con.close()
df.to_csv(sys.stdout, index=False)