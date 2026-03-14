"""
ingest_transactions.py
----------------------
Custom parser for BSB transaction CSV files.

WHY THIS EXISTS:
The raw transaction file cannot be parsed with a standard CSV reader because
ATM addresses sometimes contain commas (e.g. "Room B3, 19/F, Tung,SHEUNG WAN").
This makes the number of comma-delimited fields variable per row (14–18+),
causing naive parsers to misalign columns.

THE SOLUTION (v7 — Precision Parser):
The rightmost 10 columns are always stable and positionally fixed.
The MCC code (a 3–4 digit integer) is used as an anchor in the left-side fields.
Everything to the left of the MCC is address data; everything to the right is
the merchant name. The city/state field is always the field immediately before
the MCC.

ASSUMPTION:
    - The field immediately LEFT of the MCC is always ATM_City_State.
    - The MCC appears at index 2–6 of the left-side fields (never at 0 or 1).
    - A valid MCC is a 3–4 digit numeric string.

KNOWN LIMITATIONS:
    - ~90 rows have ATM_City_State = 'NA' or '' in the raw data. These are
      legitimate international transactions where no city data was recorded.
      They are retained as-is.
    - 1 row fails to parse (a trailing metadata line from DuckDB output).
      This is acceptable at 0.0000% failure rate across 8.2M rows.

Usage:
    from src.ingest_transactions import parse_line, COLUMNS

    with open(raw_path, 'r') as fin, open(clean_path, 'w') as fout:
        writer = csv.writer(fout)
        writer.writerow(COLUMNS)
        for line in fin:
            parsed = parse_line(line)
            if parsed:
                writer.writerow(parsed)
"""

import csv
from pathlib import Path

from config import RAW_TRANSACTIONS_CSV, TRANSACTIONS_CSV

# Output column schema - 14 fields
COLUMNS = [
    "ATM_Address",
    "ATM_City_State",
    "Merchant_Category",
    "Merchant_Name",
    "Transaction_Code",
    "Transaction_Code_Description",
    "Transaction_Type",
    "Transaction_Type_Description",
    "Transaction_Number",
    "Amount_Completed",
    "Transaction_Date",
    "Time_Local_hhmmss",
    "Recurring_Trxn",
    "CustomerID",
]


def parse_line(line: str) -> list[str] | None:
    """
    Parse a single raw transaction line into a 14-field list.

    Strategy:
        1. Split the line on commas.
        2. If exactly 14 fields - it's clean, return as-is.
        3. Otherwise, isolate the stable right-10 fields.
        4. Scan the left-remainder (indices 2–6) for the MCC anchor.
        5. Reconstruct fields relative to the MCC position:
             - ATM_Address    = everything left of city (joined back with commas)
             - ATM_City_State = field immediately left of MCC
             - Merchant_Category = the MCC field
             - Merchant_Name  = everything right of MCC (joined back with commas)

    Returns:
        list of 14 strings if successfully parsed, None otherwise.
    """
    line = line.strip()
    if not line:
        return None

    parts = line.split(",")

    # Clean path - standard 14-field row
    if len(parts) == 14:
        return parts

    # Right 10 columns are positionally stable
    right_10 = parts[-10:]
    left_remainder = parts[:-10]

    # Find the MCC anchor: first 3–4 digit numeric string at index 2–6
    mcc_index = None
    for i in range(2, min(7, len(left_remainder))):
        val = left_remainder[i].strip()
        if val.isdigit() and len(val) in (3, 4):
            mcc_index = i
            break

    if mcc_index is None:
        return None

    # Reconstruct fields relative to the anchor
    merchant_category = left_remainder[mcc_index].strip()
    merchant_name     = ",".join(left_remainder[mcc_index + 1:])
    atm_city_state    = left_remainder[mcc_index - 1].strip()
    atm_address       = ",".join(left_remainder[: mcc_index - 1])

    return [atm_address, atm_city_state, merchant_category, merchant_name] + right_10


def run(raw_path: Path = RAW_TRANSACTIONS_CSV,
        clean_path: Path = TRANSACTIONS_CSV) -> tuple[int, int]:
    """
    Parse the full raw transaction file and write the cleaned CSV.

    Args:
        raw_path:   Path to the raw BSB transaction CSV.
        clean_path: Path to write the cleaned output CSV.

    Returns:
        (success_count, failed_count) tuple.
    """
    clean_path.parent.mkdir(parents=True, exist_ok=True)

    success, failed = 0, 0
    failed_samples: list[tuple[int, str]] = []

    with open(raw_path, "r", encoding="utf-8") as fin, \
         open(clean_path, "w", encoding="utf-8", newline="") as fout:

        writer = csv.writer(fout)
        writer.writerow(COLUMNS)

        for i, line in enumerate(fin, start=1):
            if not line.strip():
                continue

            parsed = parse_line(line)
            if parsed:
                writer.writerow(parsed)
                success += 1
            else:
                failed += 1
                if len(failed_samples) < 10:
                    failed_samples.append((i, line.strip()[:120]))

    # Report
    total = success + failed
    print(f"Parsed:  {success:>10,} rows")
    print(f"Failed:  {failed:>10,} rows  ({failed / total * 100:.4f}%)")
    print(f"Output:  {clean_path}")

    if failed_samples:
        print(f"\nFailed samples (first {len(failed_samples)}):")
        for line_num, sample in failed_samples:
            print(f"  Line {line_num:,}: {sample}...")

    return success, failed


if __name__ == "__main__":
    run()