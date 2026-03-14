-- mrt_mcc_categories.sql
-- Assigns a spending category to every MCC code.
-- The top 73 codes get their category from the seed file.
-- All remaining codes default to Other.

SELECT
    m.merchant_category,
    m.mcc_label,
    COALESCE(r.category, 'Other') AS category
FROM silver.mcc_mapping m
LEFT JOIN {{ ref('mcc_category_rules') }} r
    ON m.merchant_category = r.mcc_code