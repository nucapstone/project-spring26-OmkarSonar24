# Plan

## Approach

The project aims to transform 14 raw transaction columns into engineered features per customer through aggregation, covering spending magnitude (mean, median, total), frequency, timing patterns (hour-of-day, day-of-week distributions), location diversity (unique cities, merchants), merchant category breakdowns (MCC-based), and transaction type ratios (pinned vs. pinless, recurring vs. one-time).

The modeling phase has two components. First, unsupervised clustering groups customers into 5–8 behavioral segments, evaluated using silhouette scores and other metrics, with each segment profiled into interpretable personas (e.g., "localites," "young spenders," "occasional users", "tourists", "digital shoppers"). Second, a supervised classification model predicts spending tier movement (upgrade/stable/downgrade) from one month to the next, using a train-test split by customer. Together, these outputs map customer segments to specific bank actions: early intervention, rewards targeting, personalized incentives, and local merchant promotion.

## Project Management

### Milestones

| Milestone | Status | Deliverable |
|-----------|-------------|-------------|
| Data cleaning & loading | Complete | Cleaned CSV, DuckDB tables, documented data quality issues |
| Exploratory data analysis | Complete | EDA notebooks for customers and transactions |
| Feature engineering | Currently ~40 features |   |
| Customer segmentation |  |  |
| Spending tier prediction |  |  |
| Stakeholder review |  |  |
| Final presentation |  |  |

### Risks/Limitations

- **Three-month data window:** Limited temporal span may not capture seasonal patterns or long-term behavioral shifts. 

## Stakeholder Involvement

- Stakeholder provided the data and has reviewed the project direction pivot from fraud detection to customer intelligence.
- Stakeholder meeting notes informed four business use cases: early intervention of struggling cutomers, rewards targeting, personalized incentives, and local business promotion.
- Follow-up meetings to clarify open data questions and track project status.
- Stakeholder will review final results and segment profiles before presentation.
