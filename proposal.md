# Customer Intelligence System for Bangor Savings Bank

## Team Members

- Omkar Sonar

## Project Description

### Stakeholder

Sean Reardon, Bangor Savings Bank — D&A Manager

### Story

Bank transactions record the rhythm of daily life and though masked and concise, they reveal a customer's habits, routines, and financial behavior. Analyzing these patterns allows a bank to understand who their customers truly are, not just demographically, but behaviorally.

The initial goal of this project was fraud detection and anomaly analysis. However, early exploration revealed that the transaction data lacks fraud labels (chargebacks, disputes, investigation flags), making supervised fraud detection infeasible and unsupervised anomaly detection unverifiable. This led to a pivot toward customer segmentation and spending pattern prediction, a direction that provides measurable outcomes and concrete business value.

The project now aims to build a **customer intelligence system** that segments Bangor Savings Bank customers by their transaction behavior and predicts spending pattern changes. This enables the bank to identify customers who may be struggling financially before their situation worsens, determine which customers are good candidates for the bank's rewards program (Buoy Local), deliver personalized cashback incentives aligned with actual spending habits, and promote local businesses to relevant customer segments. This system can complement the bank's existing recommendation engine with data-driven behavioral insights.

### Data

- **Customer Demographics:** 276,838 records containing relationship tenure (years/months), product holdings (deposit accounts, loans, credit cards, time deposits), active card indicators, account counts, business classification (NAICS codes), and customer flags (Bangor Wealth, Payroll, Merchant, TPS, Primary Banking).
- **Transaction Records:** 8.2M debit card transactions spanning November 2025 – January 2026, including merchant name and category (MCC codes), ATM/merchant address and city, transaction amount, date/time, transaction type codes, and recurring transaction flags.
- **Linkage:** Both datasets connect via masked CustomerIDs. 68,857 customers appear in both tables and form the core analysis population.
- **PII Status:** CustomerIDs are masked (format: BSBxxxxxx). Transaction-level fields (ATM addresses, merchant names, timestamps) carry potential re-identification risk. Data is stored locally and not shared publicly.
- **Access:** Data was provided directly by the stakeholder and is not publicly accessible.


## Capstone Goal/Contribution

The goal is to transform raw transaction and demographic data into a customer intelligence system that predicts spending behavior changes and creates actionable customer segments. Specifically, the project will engineer behavioral features from transaction data to predict spending tier movement (upgrade, stable, or downgrade), and cluster customers into interpretable segments that map to concrete bank actions — such as early intervention for financially struggling customers, rewards program targeting, personalized incentive design, and local business promotion. The contribution is a reproducible pipeline from raw bank data to business-ready customer profiles.

 
## Outcome
 
The project delivered **FinSights** - a customer spending intelligence system built on a medallion architecture (Bronze → Silver → Gold) using Python, DuckDB, dbt, and Observable Framework.
 
**What was delivered:**
- 55 behavioral features engineered per customer across spending, category, temporal, merchant, geographic, and demographic dimensions
- K-Means clustering (k=4) validated through HDBSCAN, GMM comparison, and distinctiveness count analysis
- Four customer segments identified: Active Everyday Spenders (51.5%), Lending-Engaged Loyal Customers (17.0%), Low-Frequency Big Spenders (17.0%), Low-Activity Digital Users (14.4%)
- Interactive Observable Framework dashboard with 16 validated data loaders across four pages (Overview, Trends, Customer Profiles, Recommendations)
- Segments mapped to four stakeholder-validated business use cases: Buoy Local rewards targeting, personalized cashback, early intervention, and local business promotions
- Anonymized 500-customer sample dataset for full pipeline reproducibility
 
**What was scoped out:**
- Supervised spending tier prediction (UPGRADE / STABLE / DOWNGRADE) was deferred due to timeline constraints and remains as future work, along with a 12-month data window.
