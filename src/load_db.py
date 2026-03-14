"""
load_db.py
----------
Builds the DuckDB database bronze and silver layers from processed CSV files.

Layers:
    bronze  -- all columns loaded as VARCHAR, faithful copy of source CSVs
    silver  -- typed, cleaned, business rules applied, validated

Business rules applied in silver:
    transactions  -- zero-dollar rows removed, Merchant_Category zero-padded
                     to 4 chars, Amount/Date/Time cast to correct types,
                     Transaction_Code stays VARCHAR (category code not a number)
    customers     -- duplicate CustomerIDs removed entirely, Yes/No to BOOLEAN,
                     correct types cast for all columns
    mcc_mapping   -- Merchant_Category zero-padded to 4 chars, NULLs handled
                     No Category column -- category assignment happens in dbt

Depends on (must exist before running):
    data/processed/transactions_clean.csv    from ingest_transactions.py
    data/processed/customers_clean.csv       from ingest_customers.py
    data/processed/mcc_mapping_labeled.csv   from mcc_labeler.py

Usage:
    python src/load_db.py
"""

import sys
import duckdb
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import (
    DUCKDB_PATH,
    TRANSACTIONS_CSV,
    CUSTOMERS_CSV,
    MCC_LABELED_CSV,
)


# Prerequisites 
def check_prerequisites():
    """Fail fast if any required input file is missing."""
    required = {
        "Transactions CSV": TRANSACTIONS_CSV,
        "Customers CSV":    CUSTOMERS_CSV,
        "MCC labeled CSV":  MCC_LABELED_CSV,
    }
    missing = [name for name, path in required.items() if not path.exists()]
    if missing:
        print("ERROR -- missing required files:")
        for name in missing:
            print(f"  {name}")
        print("\nRun these first:")
        print("  python src/ingest_transactions.py")
        print("  python src/ingest_customers.py")
        print("  python src/mcc_labeler.py")
        raise SystemExit(1)


# Schema setup

def setup_schemas(con):
    """
    Create bronze, silver, gold schemas.

    DROP SCHEMA CASCADE drops any existing tables inside each schema too.
    This makes the script safe to re-run -- always produces a clean result.
    """
    print("Creating schemas...")
    for schema in ("bronze", "silver", "gold"):
        con.execute(f"DROP SCHEMA IF EXISTS {schema} CASCADE")
        con.execute(f"CREATE SCHEMA {schema}")
        print(f"  {schema}")
    print()


# Bronze layer 

def load_bronze(con):
    """
    Load all three source CSVs into bronze with all columns as VARCHAR.

    Bronze is a faithful text copy of the source files.
    No type casting, no transformations, no business logic.
    Every value is stored exactly as it appears in the CSV.
    All type casting happens in silver.
    """
    print("Loading bronze layer")

    # bronze.transactions -- all columns as VARCHAR
    con.execute(f"""
        CREATE TABLE bronze.transactions AS
        SELECT * FROM read_csv(
            '{TRANSACTIONS_CSV}',
            header      = true,
            all_varchar = true
        )
    """)
    count = con.execute("SELECT COUNT(*) FROM bronze.transactions").fetchone()[0]
    print(f"  bronze.transactions       {count:>12,} rows")

    # bronze.customers -- all columns as VARCHAR
    con.execute(f"""
        CREATE TABLE bronze.customers AS
        SELECT * FROM read_csv(
            '{CUSTOMERS_CSV}',
            header      = true,
            all_varchar = true
        )
    """)
    count = con.execute("SELECT COUNT(*) FROM bronze.customers").fetchone()[0]
    print(f"  bronze.customers          {count:>12,} rows")

    # bronze.mcc_mapping -- all columns as VARCHAR
    con.execute(f"""
        CREATE TABLE bronze.mcc_mapping AS
        SELECT * FROM read_csv(
            '{MCC_LABELED_CSV}',
            header      = true,
            all_varchar = true
        )
    """)
    count = con.execute("SELECT COUNT(*) FROM bronze.mcc_mapping").fetchone()[0]
    print(f"  bronze.mcc_mapping        {count:>12,} rows")
    print()


# Silver layer 

def load_silver(con):
    """
    Build silver layer with all business rules applied.
    Every decision is documented inline.
    """
    print("Loading silver layer")

    # silver.transactions
    #
    # Rules applied:
    #   1. Remove zero-dollar transactions -- these are failed or cancelled
    #      transactions with no spending signal. Removing here means no
    #      downstream script or model ever needs to filter them.
    #
    #   2. Merchant_Category: zero-pad to 4 chars using LPAD so that JOINs
    #      with silver.mcc_mapping are always consistent.
    #      Example: '742' becomes '0742'
    #
    #   3. Amount_Completed: cast to DOUBLE to preserve decimals ($32.99 etc.)
    #      DOUBLE is appropriate here -- we compute averages and ratios,
    #      not accounting balances where exact precision is required.
    #
    #   4. Transaction_Date: cast to DATE to enable date functions such as
    #      DAYOFWEEK, MONTH, DATEDIFF in downstream queries.
    #
    #   5. Time_Local_hhmmss: cast to INTEGER. Used as FLOOR(value / 10000)
    #      to extract the hour of day (e.g. 143633 / 10000 = 14 = 2pm).
    #
    #   6. Transaction_Code stays VARCHAR -- it is a category code with only
    #      four values (0, 20, 40, 3120). No aggregation is ever done on it.
    #
    #   7. All remaining columns stay VARCHAR.
    con.execute("""
        CREATE TABLE silver.transactions AS
        SELECT
            ATM_Address,
            ATM_City_State,
            LPAD(Merchant_Category, 4, '0')        AS Merchant_Category,
            Merchant_Name,
            Transaction_Code,
            Transaction_Code_Description,
            Transaction_Type,
            Transaction_Type_Description,
            Transaction_Number,
            TRY_CAST(Amount_Completed AS DOUBLE)   AS Amount_Completed,
            TRY_CAST(Transaction_Date AS DATE)     AS Transaction_Date,
            TRY_CAST(Time_Local_hhmmss AS INTEGER) AS Time_Local_hhmmss,
            Recurring_Trxn,
            CustomerID
        FROM bronze.transactions
        WHERE TRY_CAST(Amount_Completed AS DOUBLE) > 0
    """)
    silver_txn   = con.execute("SELECT COUNT(*) FROM silver.transactions").fetchone()[0]
    bronze_txn   = con.execute("SELECT COUNT(*) FROM bronze.transactions").fetchone()[0]
    removed_txn  = bronze_txn - silver_txn
    print(f"  silver.transactions       {silver_txn:>12,} rows  ({removed_txn:,} zero-dollar removed)")

    # silver.customers
    #
    # Rules applied:
    #   1. Remove duplicate CustomerIDs entirely.
    #      BSB004527 appears twice with genuinely different data -- different
    #      ages, relationship history, and account details. This is a source
    #      system data entry error confirmed with stakeholder. Decision: remove
    #      both rows rather than guess which is correct. Any future duplicates
    #      are handled the same way automatically.
    #
    #   2. Remove rows where CustomerID is NULL or empty string.
    #
    #   3. Age: SMALLINT -- integer years, max value 126 in this dataset.
    #
    #   4. OriginalCustomerDate: DATE.
    #
    #   5. RelationshipYears, RelationshipMonths: SMALLINT.
    #
    #   6. BangorWealth, Payroll, Merchant, TPS, PlingCustomer, ABLECustomer:
    #      source file stores these as 'Yes' or 'No' strings. Convert to BOOLEAN
    #      using the expression (column = 'Yes') which evaluates to true or false.
    #      Downstream usage: WHERE BangorWealth = true
    #                        CASE WHEN Payroll THEN 1 ELSE 0 END
    #
    #   7. Account flags (DepositAccount, LoanAccount etc.) stay VARCHAR.
    #      These are 'Y' or 'N' strings that mirror BSB system encoding.
    #      Downstream usage: WHERE DepositAccount = 'Y'
    #
    #   8. NumberActiveDDAs, NumberActiveTimeDeposits, NumberActiveLoans,
    #      NumberCreditCardAccts: SMALLINT.
    con.execute("""
        CREATE TABLE silver.customers AS
        WITH duplicate_ids AS (
            SELECT CustomerID
            FROM bronze.customers
            WHERE CustomerID IS NOT NULL
              AND CustomerID != ''
            GROUP BY CustomerID
            HAVING COUNT(*) > 1
        )
        SELECT
            CustomerID,
            Individual,
            TRY_CAST(Age AS SMALLINT)                        AS Age,
            Gender,
            NAICSCode,
            TRY_CAST(OriginalCustomerDate AS DATE)           AS OriginalCustomerDate,
            TRY_CAST(RelationshipYears AS SMALLINT)          AS RelationshipYears,
            TRY_CAST(RelationshipMonths AS SMALLINT)         AS RelationshipMonths,

            (BangorWealth  = 'Yes')                          AS BangorWealth,
            (Payroll       = 'Yes')                          AS Payroll,
            (Merchant      = 'Yes')                          AS Merchant,
            (TPS           = 'Yes')                          AS TPS,
            (PlingCustomer = 'Yes')                          AS PlingCustomer,
            (ABLECustomer  = 'Yes')                          AS ABLECustomer,

            TimeDepositAccount,
            DepositAccount,
            LoanAccount,
            CreditCardAccount,
            ActiveATMCard,
            ActiveDebitCard,

            TRY_CAST(NumberActiveDDAs          AS SMALLINT) AS NumberActiveDDAs,
            TRY_CAST(NumberActiveTimeDeposits  AS SMALLINT) AS NumberActiveTimeDeposits,
            TRY_CAST(NumberActiveLoans         AS SMALLINT) AS NumberActiveLoans,
            TRY_CAST(NumberCreditCardAccts     AS SMALLINT) AS NumberCreditCardAccts,
            PrimaryBankingCustomerFlag

        FROM bronze.customers
        WHERE CustomerID IS NOT NULL
          AND CustomerID != ''
          AND CustomerID NOT IN (SELECT CustomerID FROM duplicate_ids)
    """)
    silver_cust  = con.execute("SELECT COUNT(*) FROM silver.customers").fetchone()[0]
    bronze_cust  = con.execute("SELECT COUNT(*) FROM bronze.customers").fetchone()[0]
    removed_cust = bronze_cust - silver_cust
    print(f"  silver.customers          {silver_cust:>12,} rows  ({removed_cust} removed -- nulls and duplicates)")

    # silver.mcc_mapping
    #
    # Rules applied:
    #   1. Merchant_Category: zero-pad to 4 chars so JOINs with
    #      silver.transactions are always consistent.
    #
    #   2. txn_count: cast to INTEGER.
    #
    #   3. mcc_label: empty string treated as NULL, falls back to 'Unknown'.
    #
    #   No Category column at this stage.
    #   Category assignment (mapping each MCC to Grocery, Dining, Gas etc.)
    #   happens in dbt after EDA determines the threshold and groupings.
    con.execute("""
        CREATE TABLE silver.mcc_mapping AS
        SELECT
            LPAD(Merchant_Category, 4, '0')              AS Merchant_Category,
            TRY_CAST(txn_count AS INTEGER)               AS txn_count,
            COALESCE(NULLIF(mcc_label, ''), 'Unknown')   AS mcc_label
        FROM bronze.mcc_mapping
    """)
    count = con.execute("SELECT COUNT(*) FROM silver.mcc_mapping").fetchone()[0]
    print(f"  silver.mcc_mapping        {count:>12,} rows")
    print()


# Validation 

def validate_silver(con):
    """
    Data quality assertions on the silver layer.
    Script stops if any check fails.
    """
    print("Validating silver layer...")

    checks = {
        "transactions -- no zero-dollar rows": con.execute(
            "SELECT COUNT(*) = 0 FROM silver.transactions WHERE Amount_Completed <= 0"
        ).fetchone()[0],

        "transactions -- no NULL CustomerID": con.execute(
            "SELECT COUNT(*) = 0 FROM silver.transactions WHERE CustomerID IS NULL"
        ).fetchone()[0],

        "transactions -- no NULL Transaction_Date": con.execute(
            "SELECT COUNT(*) = 0 FROM silver.transactions WHERE Transaction_Date IS NULL"
        ).fetchone()[0],

        "transactions -- Merchant_Category is always 4 chars": con.execute(
            "SELECT COUNT(*) = 0 FROM silver.transactions WHERE LENGTH(Merchant_Category) != 4"
        ).fetchone()[0],

        "transactions -- Amount_Completed is DOUBLE": con.execute(
            "SELECT typeof(Amount_Completed) = 'DOUBLE' FROM silver.transactions LIMIT 1"
        ).fetchone()[0],

        "transactions -- Transaction_Date is DATE": con.execute(
            "SELECT typeof(Transaction_Date) = 'DATE' FROM silver.transactions LIMIT 1"
        ).fetchone()[0],

        "customers -- no duplicate CustomerIDs": con.execute("""
            SELECT COUNT(*) = 0 FROM (
                SELECT CustomerID FROM silver.customers
                GROUP BY CustomerID HAVING COUNT(*) > 1
            )
        """).fetchone()[0],

        "customers -- BangorWealth is BOOLEAN": con.execute(
            "SELECT typeof(BangorWealth) = 'BOOLEAN' FROM silver.customers LIMIT 1"
        ).fetchone()[0],

        "customers -- Age is SMALLINT": con.execute(
            "SELECT typeof(Age) = 'SMALLINT' FROM silver.customers LIMIT 1"
        ).fetchone()[0],

        "mcc_mapping -- 478 unique codes": con.execute(
            "SELECT COUNT(DISTINCT Merchant_Category) = 478 FROM silver.mcc_mapping"
        ).fetchone()[0],

        "mcc_mapping -- Merchant_Category is always 4 chars": con.execute(
            "SELECT COUNT(*) = 0 FROM silver.mcc_mapping WHERE LENGTH(Merchant_Category) != 4"
        ).fetchone()[0],

        "mcc_mapping -- no NULL mcc_label": con.execute(
            "SELECT COUNT(*) = 0 FROM silver.mcc_mapping WHERE mcc_label IS NULL"
        ).fetchone()[0],
    }

    failed = []
    for name, passed in checks.items():
        status = "pass" if passed else "FAIL"
        print(f"  [{status}]  {name}")
        if not passed:
            failed.append(name)

    if failed:
        print(f"\n{len(failed)} check(s) failed -- fix before proceeding.")
        raise SystemExit(1)

    print()


# Summary 

def print_summary(con):
    """Print all tables and their row counts."""
    print("=" * 55)
    print(f"  Database: {DUCKDB_PATH}")
    print()

    tables = con.execute("""
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_schema IN ('bronze', 'silver', 'gold')
        ORDER BY table_schema, table_name
    """).fetchall()

    current_schema = None
    for schema, table in tables:
        if schema != current_schema:
            print(f"  [{schema}]")
            current_schema = schema
        count = con.execute(
            f"SELECT COUNT(*) FROM {schema}.{table}"
        ).fetchone()[0]
        print(f"    {table:<30} {count:>12,} rows")

    print()
    print("  [gold] is empty -- run feature_engineering.py to populate")
    print("=" * 55)


# Main 

def main():
    print()
    print("=" * 55)
    print("  load_db.py -- building bronze and silver layers")
    print("=" * 55)
    print()

    check_prerequisites()

    # Delete existing DB file for a guaranteed clean slate
    if DUCKDB_PATH.exists():
        DUCKDB_PATH.unlink()
        wal = Path(str(DUCKDB_PATH) + ".wal")
        if wal.exists():
            wal.unlink()
        print("Deleted existing database.\n")

    con = duckdb.connect(str(DUCKDB_PATH))

    try:
        setup_schemas(con)
        load_bronze(con)
        load_silver(con)
        validate_silver(con)

        # Gold schema created empty -- feature_engineering.py populates it
        con.execute("CREATE SCHEMA IF NOT EXISTS gold")
        print("Gold schema created (empty).\n")

        print_summary(con)

    finally:
        con.close()


if __name__ == "__main__":
    main()