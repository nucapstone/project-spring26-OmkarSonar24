# Clustering Findings -

## Data
- 58,840 individual retail customers, 55 features
- Features cover: spend amounts, category shares (grocery, dining, gas, etc.), transaction frequency, merchant behavior, demographics

## Cleaning
- **Missing values:** spend ratios → 1.0, std amount → 0, relationship years → median
- **Outliers removed:** 163 customers with ≤10 transactions but avg transaction >$1,000 (one-off payments, not behavioral)
- **Transformations:** log transform on skewed columns, percentile capping on ratios, StandardScaler on all features
- **Result:** 58,677 customers ready for clustering

## Iterative Feature Experimentation

Rather than fixing a feature set upfront, three configurations were tested to understand what drives cluster quality:

**Round 1 : All 55 features**
Full behavioral feature set after transformations. Baseline to understand raw cluster structure.

**Round 2 : Pruned to 33 features**
- Started with 41 behavioral features (product holdings like `is_primary`, `has_loan` excluded intentionally - keeps segments behavior-driven, also product holdings did not show any trends in behaviour)
- Dropped 5 highly correlated features (e.g. `transaction_count` vs `avg_transactions_per_week` = 1.0 correlation)
- Dropped 3 low-signal features on domain grounds (`max_transaction_amount`, `min_transaction_amount`, `repeat_transaction_rate`)

**Round 3 : 41 features**
Mid-point set: behavioral features only, no correlation or domain pruning applied.

## Iterative Metric Evaluation

**Step 1 : Silhouette score only** (k=2–10 on 55 features)

| k | Silhouette |
|---|---|
| 2 | 0.174 |
| 3 | 0.179 |
| 4 | 0.062 |
| 5 | 0.112 |

No single clear winner - silhouette alone wasn't sufficient to pick k confidently.

**Step 2 : Added Davies-Bouldin and Calinski-Harabasz** (55 features)

| k | Silhouette | Davies-Bouldin ↓ | Calinski-Harabasz ↑ |
|---|---|---|---|
| 2 | 0.174 | 3.41 | 4040 |
| 3 | 0.179 | 3.23 | 2940 |
| **4** | **0.062** | **3.09** | **2587** |
| 5 | 0.112 | 2.61 | 2507 |

Three metrics together gave a more consistent picture. Davies-Bouldin improves through k=4–5 then worsens. **k=4 selected** as the point of diminishing returns across all metrics.

> Silhouette scores in the 0.06–0.18 range are typical for high-dimensional customer behavioral data - customers exist on a spectrum, not in perfectly discrete groups.

## K-Means vs GMM
Both tested at k=4:
- K-Means silhouette: **0.062** | GMM silhouette: **0.075**
- GMM also tested via BIC/AIC - scores kept improving past k=4 with no clear elbow, making k selection harder
- **K-Means selected** - comparable separation, hard boundaries are easier to profile and explain to stakeholders

## The Four Segments (subject to change)

| Segment | Count | % |
|---|---|---|
| High Engagement Spenders | 8,471 | 14.4% |
| Multi-Product Loyal Customers | 30,244 | 51.5% |
| Disengaged Customers | 9,969 | 17.0% |
| Infrequent High-Value Buyers | 9,993 | 17.0% |


![Customer clusters](/figs/clustering/cluster_profiles.png)

