# Plan

## Approach

The project aims to transform raw transaction data into engineered features per customer through aggregation, covering spending magnitude (mean, median, total, std, min, max), frequency, timing patterns (weekend share, transactions per week, monthly spend ratios), location diversity (in-state vs out-of-state share), merchant behavior (unique merchants, top merchant share, repeat rates), merchant category breakdowns (MCC-based, 19 categories from 478 unique codes), and demographic indicators (age, relationship tenure, product holdings).

The modeling phase has two components. First, unsupervised clustering groups customers into behavioral segments, evaluated using silhouette scores, Davies-Bouldin index, Calinski-Harabasz index, HDBSCAN validation, GMM comparison, and a distinctiveness count metric, with each segment profiled into interpretable personas mapped to business actions. Second, a supervised classification model predicts spending tier movement (upgrade/stable/downgrade) from one month to the next, using a temporal train-test split.

Together, these outputs map customer segments to specific bank actions: early intervention, rewards targeting, personalized incentives, and local merchant promotion.

## Project Management

### Milestones

| Milestone | Status | Deliverable |
|-----------|--------|-------------|
| Data cleaning & loading | Complete | Custom CSV parser, cleaned CSVs, DuckDB bronze + silver schemas |
| Exploratory data analysis | Complete | EDA notebooks for customers and transactions, category analysis |
| MCC categorization | Complete | 478 codes parsed from Visa PDF via pdfplumber, 73 top codes mapped to 19 categories |
| Feature engineering | Complete | 55 behavioral features per customer in `gold.mrt_customer_features` via dbt |
| Data filtering & preprocessing | Complete | 58,677 individual customers after removing non-individuals and 163 outliers |
| Customer segmentation | Complete | K-Means k=4, validated with HDBSCAN, GMM, and distinctiveness counts |
| Segment profiling | Complete | Four named segments mapped to four business use cases |
| Interactive dashboard | Complete | Observable Framework, 16 data loaders, 4 pages (Overview, Trends, Profiles, Recommendations) |
| Data validation | Complete | All loaders scoped to 58,677 customers, totals verified end-to-end |
| Data reproducibility | Complete | Anonymized 500-customer sample in `data/sample/`, pipeline auto-detects and falls back |
| Stakeholder review | Complete | Pivot validated, shaped use cases, flagged January caveat |
| Final presentation | Complete | 10-minute video with slides and live dashboard demo |
| Spending tier prediction | Deferred | Scoped out due to timeline - documented as future work |

### Risks/Limitations
- **65-day data window:** Observation period (Nov 20 – Jan 24) includes holiday spending spike and post-holiday pullback. Patterns may not generalize to a full year.
- **Customer coverage:** 58,677 of ~128,000 transacting customers had both transaction and demographic records. ~59,000 additional customers lacked demographics and were excluded.
- **MCC ambiguity:** Some merchant category codes are ambiguous (e.g., Bookstores spans Amazon to physical retailers). Requires ongoing stakeholder validation.
- **Soft cluster boundaries:** HDBSCAN confirmed no naturally discrete groups exist in the data. Segments are useful business groupings, not hard categories.
- **Supervised modeling deferred:** Spending tier prediction (UPGRADE / STABLE / DOWNGRADE) was planned but deferred due to timeline constraints.

