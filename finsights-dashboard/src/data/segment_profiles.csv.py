import duckdb
import pandas as pd
import numpy as np
import sys

con = duckdb.connect("../data/capstone.duckdb", read_only=True)

df = con.execute("""
    SELECT f.*, c.cluster, c.cluster_name
    FROM gold.mrt_customer_features f
    JOIN gold.mrt_customer_clusters c
        ON f.customer_id = c.customer_id
""").fetchdf()

con.close()

# Identify feature columns
exclude = ['customer_id', 'Individual', 'cluster', 'cluster_name']
features = [c for c in df.columns if c not in exclude and df[c].dtype in ['float64', 'int64', 'float32', 'int32']]

# Compute z-scores: (cluster_mean - population_mean) / population_std
pop_mean = df[features].mean()
pop_std = df[features].std()
cluster_means = df.groupby('cluster_name')[features].mean()

rows = []
for cluster_name in cluster_means.index:
    for feature in features:
        z = (cluster_means.loc[cluster_name, feature] - pop_mean[feature]) / pop_std[feature]
        rows.append({
            'cluster_name': cluster_name,
            'feature': feature,
            'cluster_mean': round(cluster_means.loc[cluster_name, feature], 4),
            'population_mean': round(pop_mean[feature], 4),
            'z_score': round(z, 4)
        })

result = pd.DataFrame(rows)
result.to_csv(sys.stdout, index=False)