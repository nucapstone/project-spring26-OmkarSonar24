# FinSights: Customer Spending Intelligence System

**DS5500 Capstone Project** | Northeastern University | Spring 2026

**Author:** Omkar Sonar

**Professor:** Philip Bogden, PhD

**Stakeholder:** Sean Reardon, Data & Analytics Manager, Bangor Savings Bank



---

## Project Overview

Bank transactions record the rhythm of daily life. Though masked and concise, they reveal a customer's habits, routines, and financial behavior.

The initial goal of this project was fraud detection. However, early exploration revealed that the dataset contained no fraud labels, making supervised fraud detection infeasible. This led to a pivot toward **customer segmentation and spending intelligence**, a direction that provides measurable outcomes and concrete business value.

The project builds a **customer intelligence system** that segments Bangor Savings Bank customers by debit card transaction behavior and predicts spending tier movement (UPGRADE / STABLE / DOWNGRADE). This enables the bank to:

1. Identify customers who may be **struggling financially** before their situation worsens
2. Determine which customers are good candidates for the **Buoy Local rewards program**
3. Deliver **personalized cashback incentives** aligned with actual spending habits
4. **Promote local businesses** to relevant customer segments

This is a **proof of concept**.

---

## Data

| Dataset | Records | Description |
|---|---|---|
| Customer Demographics | 276,838 | Profiles including relationship tenure, product holdings, active status |
| Debit Card Transactions | 8,234,091 | Merchant name/category, ATM location, amount, date/time |

Both datasets share a masked `CustomerID` as the linking identifier. The observation window covers approximately 65 days (November 2025 to January 2026).

**Note:** Raw data files are private (provided by Bangor Savings Bank) and are not included in this repository. To reproduce the pipeline, place the original files in `data/raw/` as described in the setup instructions below.

![Customer data](/figs/customers_dt.png)
![Transactions data](/figs/transactions_dt.png)

---

## Project Structure

```
project-spring26-OmkarSonar24/
│
├── src/                              # Pipeline scripts (run in order)
│   ├── config.py                     #   All file paths and constants
│   ├── ingest_transactions.py        #   Step 1: Raw CSV -> transactions_clean.csv
│   ├── ingest_customers.py           #   Step 2: Raw Excel -> customers_clean.csv
│   ├── mcc_labeler.py                #   Step 3: Visa PDF -> mcc_mapping_labeled.csv
│   └── load_db.py                    #   Step 4: CSVs -> DuckDB bronze + silver layers
│
├── capstone_dbt/                     # dbt project (gold layer, Step 5)
│   ├── models/
│   │   ├── marts/
│   │   │   ├── mrt_mcc_categories.sql
│   │   │   └── mrt_customer_features.sql
│   │   └── sources.yml               #   Documents upstream silver tables
│   ├── seeds/
│   │   └── mcc_category_rules.csv    #   73 top MCC category assignments
│   ├── macros/
│   │   └── generate_schema_name.sql
│   ├── profiles_template.yml         #   Template for ~/.dbt/profiles.yml
│   └── dbt_project.yml
│
├── notebooks/                        # Analysis notebooks (run in order)
│   ├── 01_customers_eda.ipynb        #   Customer demographics EDA
│   ├── 02_transactions_eda.ipynb     #   Transaction-level EDA
│   ├── 03_stakeholder_analysis.ipynb #   Business questions for stakeholder
│   ├── 04_clustering.ipynb           #   K-Means segmentation (k=4)
│   └── 05_features_selection.ipynb   #   Feature pruning experiments
│
├── data/                             # Data directory (gitignored)
│   ├── raw/                          #   Original CSV + XLSX from BSB
│   └── processed/                    #   Generated clean CSVs
│
├── figs/                             # All visualizations
│   ├── eda/                          #   EDA plots (customers, transactions)
│   ├── clustering/                   #   Cluster selection and profiles
│   └── feature_selection/            #   Correlation heatmap
│
├── docs/                             # Project documentation
│   ├── data_issues.md                #   Data quality issues and decisions
│   └── data_summary.md              #   Project phases and observations
│
├── misc/                             # Reference materials
│   └── visa-merchant-data-standards-manual.pdf
│
├── presentations/                    # Slide decks
│   ├── class/                        #   Check-in presentations
│   └── stakeholder/                  #   BSB meeting materials
│
├── pyproject.toml                    # Python dependencies (uv)
├── uv.lock                           # Locked dependency versions
└── README.md
```

---

## Setup and Reproduction

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager (recommended), or pip
- Raw data files from Bangor Savings Bank

### Step 1: Clone and install dependencies

**Using uv (recommended):**

```bash
git clone <repo-url>
cd project-spring26-OmkarSonar24
uv sync
```

**Using pip (alternative):**

```bash
git clone <repo-url>
cd project-spring26-OmkarSonar24
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Both approaches create a `.venv` virtual environment and install all packages from `pyproject.toml`, including dbt-core and dbt-duckdb.

### Step 2: Activate the environment

```bash
source .venv/bin/activate
```

### Step 3: Place raw data files

Since the data directory is gitignored, create it and add the original BSB files:

```bash
mkdir -p data/raw data/processed
```

Copy the files into `data/raw/`:

```
data/raw/
├── OmkarCapstone_Final_ArchivePassportData_20260123.csv
└── OmkarCustomerDemographics.xlsx
```

### Step 4: Run the data pipeline

Run these four scripts in order from the project root:

```bash
# Parse transactions
python src/ingest_transactions.py

# Convert customer demographics from Excel to CSV
python src/ingest_customers.py

# Extract and label MCC codes from Visa PDF
python src/mcc_labeler.py

# Build DuckDB database (bronze + silver layers)
python src/load_db.py
```

Expected outputs:

| File | Location | Rows |
|---|---|---|
| transactions_clean.csv | data/processed/ | 8,234,091 |
| customers_clean.csv | data/processed/ | 276,838 |
| mcc_mapping_labeled.csv | data/processed/ | 478 MCC codes |
| capstone.duckdb | data/ | Bronze + silver schemas |

### Step 5: Configure and run dbt (gold layer)

dbt (data build tool) transforms the silver layer into analysis-ready feature tables. It was installed in Step 1 as part of the project dependencies.

**5a.** Create the dbt profiles file. A template is included in the repo:

```bash
mkdir -p ~/.dbt
cp capstone_dbt/profiles_template.yml ~/.dbt/profiles.yml
```

**5b.** Edit `~/.dbt/profiles.yml` and replace the placeholder path with your actual project location:

```bash
# To find your path, run from the project root:
echo $(pwd)/data/capstone.duckdb
```

Paste that full path as the `path` value in `profiles.yml`.

**5c.** All dbt commands must be run from inside the `capstone_dbt/` directory:

```bash
cd capstone_dbt
dbt debug          # verify connection (look for "Connection test: OK")
dbt seed           # load mcc_category_rules (73 rows into gold schema)
dbt run            # build mrt_mcc_categories + mrt_customer_features
cd ..
```

If `dbt debug` fails, the most common cause is an incorrect path in `profiles.yml`.

### Step 6: Register Jupyter kernel and run notebooks

```bash
python -m ipykernel install --user --name=capstone --display-name "Python (capstone)"
jupyter notebook
```

Run notebooks in order (01 through 05), selecting the **Python (capstone)** kernel in each.

---

## Database Architecture

The project uses a **medallion architecture** in DuckDB:

| Layer | Schema | Built By | Description |
|---|---|---|---|
| Bronze | `bronze.*` | `src/load_db.py` | Raw data loaded as-is (all VARCHAR) |
| Silver | `silver.*` | `src/load_db.py` | Cleaned, typed, deduplicated |
| Gold | `gold.*` | `dbt run` | Feature-engineered, analysis-ready |

Key table: `gold.mrt_customer_features` contains 68,582 customers with 57 columns.

---

## Key Technical Decisions

| Decision | Rationale |
|---|---|
| Custom CSV parser | Raw transaction file has embedded commas in ATM addresses. Standard parsers fail. MCC code used as positional anchor. |
| Pivot from fraud to segmentation | No fraud labels in dataset. Proactively surfaced to stakeholder as analytical integrity. |
| K-Means k=4 over GMM (as of now) | Silhouette 0.110. Business-interpretable segments. |
| 57 features for clustering | Three-way comparison (57 vs 41 vs 33) showed full feature set outperforms pruned sets at all business-relevant k values. |
