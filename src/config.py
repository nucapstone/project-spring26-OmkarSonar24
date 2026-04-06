from pathlib import Path

# Project root 
BASE_DIR = Path(__file__).resolve().parent.parent

# Directory layout
RAW_DIR       = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
MISC_DIR      = BASE_DIR / "misc"

# Raw input files
RAW_TRANSACTIONS_CSV = RAW_DIR / "OmkarCapstone_Final_ArchivePassportData_20260123.csv"
CUSTOMERS_EXCEL      = RAW_DIR / "OmkarCustomerDemographics.xlsx"
VISA_PDF             = MISC_DIR / "visa-merchant-data-standards-manual.pdf"

# Processed outputs
TRANSACTIONS_CSV  = PROCESSED_DIR / "transactions_clean.csv"
CUSTOMERS_CSV     = PROCESSED_DIR / "customers_clean.csv"
MCC_INPUT_CSV     = BASE_DIR / "data" / "mcc_mapping.csv"
MCC_LABELED_CSV   = PROCESSED_DIR / "mcc_mapping_labeled.csv"

# Sample data (for reproducibility purposes)
SAMPLE_DIR = BASE_DIR / "data" / "sample"
SAMPLE_CUSTOMERS = SAMPLE_DIR / "customers_sample.csv"
SAMPLE_TRANSACTIONS = SAMPLE_DIR / "transactions_sample.csv"

USE_SAMPLE = not PROCESSED_DIR.exists() or not TRANSACTIONS_CSV.exists()

if USE_SAMPLE:
    TRANSACTIONS_CSV = SAMPLE_TRANSACTIONS
    CUSTOMERS_CSV    = SAMPLE_CUSTOMERS
    MCC_LABELED_CSV  = SAMPLE_DIR / "mcc_mapping_labeled.csv"

# Database
DUCKDB_PATH           = BASE_DIR  / "data" / "capstone.duckdb"