"""
mcc_labeler.py
--------------
Extracts all MCC codes from the transaction CSV, labels them using
the Visa Merchant Data Standards Manual PDF, and saves the result.

Steps:
    1. Read transactions_clean.csv and extract all unique MCC codes
       with their transaction counts --> saves to data/mcc_mapping.csv
    2. Read the Visa PDF and build a code --> description dictionary
    3. Match each MCC code against the PDF dictionary
    4. Apply manual labels for any codes not found in the PDF
    5. Save the final labeled mapping --> data/processed/mcc_mapping_labeled.csv

Usage:
    python src/mcc_labeler.py

Requirements:
    pip install pdfplumber pandas openpyxl
"""

import re
import csv
import pdfplumber
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import VISA_PDF, MCC_INPUT_CSV, MCC_LABELED_CSV, TRANSACTIONS_CSV


# Manual labels 
# Codes not found in the Visa PDF — looked up manually
MANUAL_LABELS = {
    '6141': 'Personal Finance Companies / Consumer Loans',
    '6411': 'Insurance Agents, Brokers and Services',
    '0474': 'Unknown',
    '6050': 'Quasi Cash - Member Financial Institution',
    '6534': 'Money Transfer - Member Financial Institution',
    '0863': 'Unknown',
    '0170': 'Unknown',
    '2060': 'Unknown',
    '0302': 'Unknown',
    '2217': 'Unknown',
    '0655': 'Unknown',
}


# Step 1: Extract unique MCC codes from transactions CSV

def extract_mcc_codes(transactions_csv, output_csv):
    """
    Read transactions_clean_v2.csv and count how many times
    each MCC code appears. Saves result to data/mcc_mapping.csv.

    This gives us the list of codes we need to label.
    """
    print(f"Reading transactions: {transactions_csv}")

    if not transactions_csv.exists():
        raise FileNotFoundError(
            f"Transactions CSV not found: {transactions_csv}\n"
            "Run ingest_transactions.py first."
        )

    # Count each MCC code using csv module - avoids loading 8M rows into memory
    mcc_counts = {}
    with open(transactions_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = row.get("Merchant_Category", "").strip()
            if code:
                mcc_counts[code] = mcc_counts.get(code, 0) + 1

    # Save as CSV
    df = pd.DataFrame([
        {"Merchant_Category": code, "txn_count": count}
        for code, count in mcc_counts.items()
    ]).sort_values("txn_count", ascending=False)

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv, index=False)

    print(f"  Found {len(df)} unique MCC codes")
    print(f"  Saved to {output_csv}\n")

    return df


# Step 2: Extract labels from Visa PDF 

def clean_text(text):
    """Replace special Unicode characters that appear in the Visa PDF."""
    replacements = {
        '\u2013': '-',
        '\u2014': '-',
        '\u2018': "'",
        '\u2019': "'",
        '\u201c': '"',
        '\u201d': '"',
        '\xa0':   ' ',
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text


def extract_labels_from_pdf(pdf_path):
    """
    Read the Visa Merchant Data Standards Manual PDF and build
    a dictionary of {mcc_code: description}.

    Uses two extraction strategies:
      1. Table extraction - most codes appear in tables (col 0 = code, col 3 = label)
      2. Text extraction - some codes appear as plain text lines
      3. Reverse pattern - some codes appear on their own line with label above
    """
    print(f"Reading Visa PDF: {pdf_path}")

    if not pdf_path.exists():
        raise FileNotFoundError(f"Visa PDF not found: {pdf_path}")

    mcc_dict = {}

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:

            # Strategy 1 - table extraction (col 0 = code, col 3 = description)
            for table in page.extract_tables():
                for row in table:
                    if row and len(row) >= 4:
                        code = str(row[0]).strip() if row[0] else ''
                        desc = clean_text(str(row[3]).strip()) if row[3] else ''
                        if re.match(r'^\d{4}$', code) and len(desc) > 3:
                            if code not in mcc_dict:
                                mcc_dict[code] = desc

            # Strategy 2 & 3 - text extraction
            text = page.extract_text()
            if not text:
                continue

            text = clean_text(text)
            lines = text.split('\n')

            for j, line in enumerate(lines):
                line = line.strip()

                # Strategy 2: "5411 Grocery Stores and Supermarkets"
                match = re.match(r'^(\d{4})\s([A-Z][^0-9].+)$', line)
                if match:
                    code = match.group(1)
                    desc = match.group(2).strip()
                    if code not in mcc_dict:
                        mcc_dict[code] = desc
                    continue

                # Strategy 3: bare code on its own line, label on line above
                # e.g.  "Bus Lines"
                #       "4131"
                if re.match(r'^\d{4}$', line) and j > 0:
                    code = line
                    prev = lines[j - 1].strip()
                    if prev and re.match(r'^[A-Z]', prev) and not re.match(r'^\d', prev):
                        if code not in mcc_dict:
                            mcc_dict[code] = prev

    print(f"  Extracted {len(mcc_dict)} MCC labels from PDF\n")
    return mcc_dict


# Step 3: Match codes to labels and save 

def label_and_save(mcc_input_csv, output_csv, mcc_dict, manual_labels):
    """
    Match each MCC code against the PDF dictionary and manual labels.
    Saves the final labeled CSV.
    """
    df = pd.read_csv(mcc_input_csv)
    df['Merchant_Category'] = df['Merchant_Category'].astype(str).str.strip()

    # Zero-pad to 4 digits for matching (e.g. 742 --> 0742)
    df['mcc_padded'] = df['Merchant_Category'].str.zfill(4)

    # Match against PDF labels
    df['mcc_label'] = df['mcc_padded'].map(mcc_dict)

    # Apply manual labels for codes not in the PDF
    for code, label in manual_labels.items():
        mask = df['mcc_padded'] == code.zfill(4)
        df.loc[mask, 'mcc_label'] = label

    # Report
    matched   = df['mcc_label'].notna().sum()
    unmatched = df['mcc_label'].isna().sum()
    print(f"  Matched:   {matched} / {len(df)}")
    print(f"  Unmatched: {unmatched}")

    if unmatched > 0:
        print("\n  These codes were not found in the PDF or manual labels.")
        print("  Add them to MANUAL_LABELS in this script:\n")
        print(df[df['mcc_label'].isna()][['Merchant_Category', 'txn_count']].to_string())

    # Save - keep mcc_padded as the canonical code
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df[['mcc_padded', 'txn_count', 'mcc_label']].rename(
        columns={'mcc_padded': 'Merchant_Category'}
    ).to_csv(output_csv, index=False, encoding='utf-8')

    print(f"\n  Saved to {output_csv}")


# Main 

if __name__ == "__main__":
    print("=" * 50)
    print("  mcc_labeler.py")
    print("=" * 50)
    print()

    print("Step 1 - extracting unique MCC codes from transactions CSV")
    extract_mcc_codes(TRANSACTIONS_CSV, MCC_INPUT_CSV)

    print("Step 2 - extracting labels from Visa PDF")
    mcc_dict = extract_labels_from_pdf(VISA_PDF)

    print("Step 3 - matching codes to labels")
    label_and_save(MCC_INPUT_CSV, MCC_LABELED_CSV, mcc_dict, MANUAL_LABELS)

    print()
    print("Done.")