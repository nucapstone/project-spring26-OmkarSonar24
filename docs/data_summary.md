# Project Phases

---

## Phase 1 - Cleaning

Got the data (transactions - csv and customers - xlsx)

**With transactions:**
- Added headers to the data
- Extra commas in address fields and had to parse that out to fit the data in 14 header columns

**With customers:**
- Empty rows cleared
- File converted from xlsx to csv

---

## Phase 2 - Loading

Created `capstone_data.duckdb`
- Two tables created - `transactions_v2` and `customers`

---

## Phase 3 - EDA, Data Verification and Info Gathering

**Observations and Discrepancies**

| Observation | Detail |
|---|---|
| Duplicate customerID in customers | Ignoring both of them after discussing with Sean |
| ATM_City_State blank | Initially this count was 928 (incorrect parsing of csv). With correct parsing, this count is 90(23) hence table is `transactions_v2` |
| Zero dollar records | Around 96k. After discussing with Sean, these are likely failures so ignoring them |
| Age observations | 139 customers above 100 with max being 126; 40,533 customers aged 0 |
| Gender observations | M, F, Blank, Other, Undeclared |
| Date Range | 8th Sept 2025 to 24th Jan 2026 (primarily from 21st Nov) |
| Customers common in both datasets | 68,857 |
| Unique merchant codes | 478 |
| Approx | 18 weekends, 46 weekdays |

---

## Phase 4 - Feature Engineering

On the basis of:
- Spending aggregates
- Category shares
- Temporal features
- Merchant categories
- Demographic features
- Trend features

![Features_a](/figs/features_a.png)

![Features_b](/figs/features_b.png)