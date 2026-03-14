"""
ingest_customers.py
-------------------
Converts the raw BSB customer demographics Excel file to a clean CSV.

What it does:
    1. Reads OmkarCustomerDemographics.xlsx
    2. Drops fully empty rows (2 rows in the source file)
    3. Validates row count and columns
    4. Saves to data/processed/customers_clean.csv

What it does NOT do:
    - No type casting (that happens in load_db.py silver layer)
    - No deduplication (that happens in load_db.py silver layer)
    - No normalization of Yes/No values (that happens in load_db.py silver layer)

The raw Excel is preserved exactly. This script only converts format.

Usage:
    python src/ingest_customers.py
"""

import sys
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import CUSTOMERS_EXCEL, CUSTOMERS_CSV

EXPECTED_COLUMNS = [
    "CustomerID",
    "Individual",
    "Age",
    "Gender",
    "NAICSCode",
    "OriginalCustomerDate",
    "RelationshipYears",
    "RelationshipMonths",
    "BangorWealth",
    "Payroll",
    "Merchant",
    "TPS",
    "PlingCustomer",
    "ABLECustomer",
    "TimeDepositAccount",
    "DepositAccount",
    "LoanAccount",
    "CreditCardAccount",
    "ActiveATMCard",
    "ActiveDebitCard",
    "NumberActiveDDAs",
    "NumberActiveTimeDeposits",
    "NumberActiveLoans",
    "NumberCreditCardAccts",
    "PrimaryBankingCustomerFlag",
]


def ingest(excel_path=CUSTOMERS_EXCEL, csv_path=CUSTOMERS_CSV):
    """
    Read Excel, drop empty rows, validate, save to CSV.

    Returns:
        int: number of rows written
    """
    print(f"Reading: {excel_path}")

    if not excel_path.exists():
        raise FileNotFoundError(f"Excel file not found: {excel_path}")

    # Read Excel — keep all columns as-is, no type inference
    df = pd.read_excel(excel_path, dtype=str)
    raw_count = len(df)
    print(f"  Raw rows:      {raw_count:>10,}")

    # Drop fully empty rows
    df = df.dropna(how="all")
    dropped = raw_count - len(df)
    if dropped > 0:
        print(f"  Dropped empty: {dropped:>10,} rows")

    # Validate columns
    missing_cols = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing expected columns: {missing_cols}")

    extra_cols = [c for c in df.columns if c not in EXPECTED_COLUMNS]
    if extra_cols:
        print(f"  Warning — unexpected columns found: {extra_cols}")

    # Keep only expected columns in defined order
    df = df[EXPECTED_COLUMNS]

    # Save
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(csv_path, index=False, encoding="utf-8")

    print(f"  Written rows:  {len(df):>10,}")
    print(f"  Output:        {csv_path}")

    return len(df)


if __name__ == "__main__":
    ingest()