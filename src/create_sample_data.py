import pandas as pd
from pathlib import Path

SAMPLE_SIZE = 500
SEED = 42


customers = pd.read_csv("data/processed/customers_clean.csv")
transactions = pd.read_csv("data/processed/transactions_clean.csv")

individuals = customers[customers["Individual"] == 'Y']
has_txns = individuals["CustomerID"].isin(transactions["CustomerID"])
eligible = individuals[has_txns]

sample_cust = eligible.sample(n = SAMPLE_SIZE, random_state = SEED)
sample_ids = set(sample_cust["CustomerID"])

print(f"Eligible customers (Individual + has transactions): {len(eligible):,}")

sample_txns = transactions[transactions["CustomerID"].isin(sample_ids)]

Path("data/sample").mkdir(parents = True, exist_ok = True)
sample_cust.to_csv("data/sample/customers_sample.csv", index = False)
sample_txns.to_csv("data/sample/transactions_sample.csv", index = False)

print(f"Customers:    {len(sample_cust):,}")
print(f"Transactions: {len(sample_txns):,}")
