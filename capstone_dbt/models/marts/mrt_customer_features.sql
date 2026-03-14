-- mrt_customer_features.sql
-- -------------------------
-- Builds the customer feature matrix for clustering and segmentation.
-- One row per customer. All customers who made at least one transaction
-- between 2025-11-20 and 2026-01-25.
--
-- Individual flag is included as an identifier column.
-- Filter to Individual = 'Y' in the analysis notebook for clustering.
--
-- Feature count: 55
--   Spending aggregates:  7
--   Category shares:     19
--   Temporal:             4
--   Merchant behavior:    5
--   Demographics:        18
--   Trends:               2
--
-- Date window: 2025-11-20 to 2026-01-25
-- Zero-dollar transactions already removed in silver layer.

with

-- -------------------------------------------------------------------------
-- 1. Spending aggregates (7 features)
-- -------------------------------------------------------------------------
spending_agg as (
    select
        t.CustomerID                            as customer_id,
        sum(t.Amount_Completed)                 as total_spend,
        count(*)                                as transaction_count,
        round(avg(t.Amount_Completed), 2)       as avg_transaction_amount,
        round(median(t.Amount_Completed), 2)    as median_transaction_amount,
        round(stddev(t.Amount_Completed), 2)    as std_transaction_amount,
        max(t.Amount_Completed)                 as max_transaction_amount,
        min(t.Amount_Completed)                 as min_transaction_amount
    from silver.transactions t
    inner join silver.customers c
        on t.CustomerID = c.CustomerID
    where t.Transaction_Date between '2025-11-20' and '2026-01-25'
    group by t.CustomerID
),

-- -------------------------------------------------------------------------
-- 2. Category shares (19 features)
-- Spend share = category spend / total spend per customer.
-- Other captures: Other category + any unmatched MCC codes (NULL join).
-- Electronics/Computers has its own share column.
-- -------------------------------------------------------------------------
category_shares as (
    select
        t.CustomerID as customer_id,

        round(sum(case when m.category = 'Grocery'
            then t.Amount_Completed else 0 end)
            / nullif(sum(t.Amount_Completed), 0), 4) as grocery_share,

        round(sum(case when m.category = 'Dining'
            then t.Amount_Completed else 0 end)
            / nullif(sum(t.Amount_Completed), 0), 4) as dining_share,

        round(sum(case when m.category = 'Gas'
            then t.Amount_Completed else 0 end)
            / nullif(sum(t.Amount_Completed), 0), 4) as gas_share,

        round(sum(case when m.category = 'Digital/Subscriptions'
            then t.Amount_Completed else 0 end)
            / nullif(sum(t.Amount_Completed), 0), 4) as digital_share,

        round(sum(case when m.category = 'Electronics/Computers'
            then t.Amount_Completed else 0 end)
            / nullif(sum(t.Amount_Completed), 0), 4) as electronics_share,

        round(sum(case when m.category = 'Telecom/Cable'
            then t.Amount_Completed else 0 end)
            / nullif(sum(t.Amount_Completed), 0), 4) as telecom_share,

        round(sum(case when m.category = 'Retail'
            then t.Amount_Completed else 0 end)
            / nullif(sum(t.Amount_Completed), 0), 4) as retail_share,

        round(sum(case when m.category = 'Healthcare'
            then t.Amount_Completed else 0 end)
            / nullif(sum(t.Amount_Completed), 0), 4) as healthcare_share,

        round(sum(case when m.category = 'Pets'
            then t.Amount_Completed else 0 end)
            / nullif(sum(t.Amount_Completed), 0), 4) as pets_share,

        round(sum(case when m.category = 'Home/Hardware'
            then t.Amount_Completed else 0 end)
            / nullif(sum(t.Amount_Completed), 0), 4) as home_share,

        round(sum(case when m.category = 'Automotive'
            then t.Amount_Completed else 0 end)
            / nullif(sum(t.Amount_Completed), 0), 4) as automotive_share,

        round(sum(case when m.category = 'Clothing'
            then t.Amount_Completed else 0 end)
            / nullif(sum(t.Amount_Completed), 0), 4) as clothing_share,

        round(sum(case when m.category = 'Entertainment/Leisure'
            then t.Amount_Completed else 0 end)
            / nullif(sum(t.Amount_Completed), 0), 4) as entertainment_share,

        round(sum(case when m.category = 'Financial Services'
            then t.Amount_Completed else 0 end)
            / nullif(sum(t.Amount_Completed), 0), 4) as financial_share,

        round(sum(case when m.category = 'Personal Care'
            then t.Amount_Completed else 0 end)
            / nullif(sum(t.Amount_Completed), 0), 4) as personal_care_share,

        round(sum(case when m.category = 'Transportation'
            then t.Amount_Completed else 0 end)
            / nullif(sum(t.Amount_Completed), 0), 4) as transport_share,

        round(sum(case when m.category = 'Utilities'
            then t.Amount_Completed else 0 end)
            / nullif(sum(t.Amount_Completed), 0), 4) as utilities_share,

        round(sum(case when m.category = 'Government/Community'
            then t.Amount_Completed else 0 end)
            / nullif(sum(t.Amount_Completed), 0), 4) as government_share,

        -- Other: catches Other category and any unmatched MCCs (NULL)
        round(sum(case when m.category = 'Other' or m.category is null
            then t.Amount_Completed else 0 end)
            / nullif(sum(t.Amount_Completed), 0), 4) as other_share

    from silver.transactions t
    left join {{ ref('mrt_mcc_categories') }} m
        on t.Merchant_Category = m.merchant_category
    where t.Transaction_Date between '2025-11-20' and '2026-01-25'
    group by t.CustomerID
),

-- -------------------------------------------------------------------------
-- 3. Temporal features (4 features)
-- avg_transactions_per_week uses dynamic window calculation.
-- Daily spend ratios use active days per month as denominator to
-- normalize for unequal days -- Nov only has ~10 days of data.
-- -------------------------------------------------------------------------
temporal as (
    select
        CustomerID as customer_id,

        -- Share of transactions on weekends
        -- DuckDB DAYOFWEEK: 0 = Sunday, 6 = Saturday
        round(
            sum(case when dayofweek(Transaction_Date) in (0, 6)
                then 1 else 0 end) * 1.0 / count(*),
        4) as weekend_share,

        -- Avg transactions per week
        -- Window = 2025-11-20 to 2026-01-25, calculated dynamically
        round(
            count(*) / (datediff('day', DATE '2025-11-20', DATE '2026-01-25') / 7.0),
        2) as avg_transactions_per_week,

        -- Dec vs Nov daily spend intensity
        round(
            (sum(case when month(Transaction_Date) = 12
                then Amount_Completed else 0 end)
            / nullif(count(distinct case when month(Transaction_Date) = 12
                then Transaction_Date end), 0))
            /
            nullif(
                sum(case when month(Transaction_Date) = 11
                    then Amount_Completed else 0 end)
                / nullif(count(distinct case when month(Transaction_Date) = 11
                    then Transaction_Date end), 0)
            , 0),
        4) as dec_to_nov_daily_spend_ratio,

        -- Jan vs Dec daily spend intensity
        round(
            (sum(case when month(Transaction_Date) = 1
                then Amount_Completed else 0 end)
            / nullif(count(distinct case when month(Transaction_Date) = 1
                then Transaction_Date end), 0))
            /
            nullif(
                sum(case when month(Transaction_Date) = 12
                    then Amount_Completed else 0 end)
                / nullif(count(distinct case when month(Transaction_Date) = 12
                    then Transaction_Date end), 0)
            , 0),
        4) as jan_to_dec_daily_spend_ratio

    from silver.transactions
    where Transaction_Date between '2025-11-20' and '2026-01-25'
    group by CustomerID
),

-- -------------------------------------------------------------------------
-- 4. Merchant behavior (5 features)
-- -------------------------------------------------------------------------
merchant as (
    select
        customer_id,
        count(distinct Merchant_Name)                       as unique_merchants,
        round(max(merchant_total)
            / nullif(sum(merchant_total), 0), 4)            as top_merchant_share,
        round(
            sum(case when merchant_visits > 1 then 1 else 0 end) * 1.0
            / nullif(count(*), 0),
        4) as repeat_merchant_rate,
        round(
            sum(case when merchant_visits > 1
                then merchant_visits - 1 else 0 end) * 1.0
            / nullif(sum(merchant_visits), 0),
        4) as repeat_transaction_rate,
        round(
            sum(merchant_visits) * 1.0 / nullif(count(*), 0),
        2) as avg_visits_per_merchant

    from (
        select
            CustomerID              as customer_id,
            Merchant_Name,
            count(*)                as merchant_visits,
            sum(Amount_Completed)   as merchant_total
        from silver.transactions
        where Transaction_Date between '2025-11-20' and '2026-01-25'
        group by CustomerID, Merchant_Name
    ) sub
    group by customer_id
),

-- -------------------------------------------------------------------------
-- 5. Demographics (18 features)
-- BangorWealth, Payroll, PlingCustomer, ABLECustomer are BOOLEAN in silver.
-- Account flags (DepositAccount etc.) are VARCHAR Y/N in silver.
-- Individual included as identifier -- not a feature.
-- -------------------------------------------------------------------------
demographics as (
    select
        c.CustomerID                                                    as customer_id,
        c.Individual,
        c.Age,
        c.RelationshipYears,
        case when c.Gender = 'M' then 1 else 0 end                     as is_male,
        case when c.Gender = 'F' then 1 else 0 end                     as is_female,
        c.NumberActiveDDAs,
        c.NumberActiveTimeDeposits,
        c.NumberActiveLoans,
        c.NumberCreditCardAccts,
        case when c.DepositAccount = 'Y' then 1 else 0 end             as has_deposit,
        case when c.LoanAccount = 'Y' then 1 else 0 end                as has_loan,
        case when c.CreditCardAccount = 'Y' then 1 else 0 end          as has_creditcard,
        case when c.ActiveATMCard = 'Y' then 1 else 0 end              as has_atm,
        case when c.ActiveDebitCard = 'Y' then 1 else 0 end            as has_debit,
        case when c.PrimaryBankingCustomerFlag = 'Y' then 1 else 0 end as is_primary,
        case when c.BangorWealth = true then 1 else 0 end              as is_wealth,
        case when c.Payroll = true then 1 else 0 end                   as is_payroll,
        case when c.PlingCustomer = true then 1 else 0 end             as is_pling,
        case when c.ABLECustomer = true then 1 else 0 end              as is_able

    from silver.customers c
    inner join (
        select distinct CustomerID
        from silver.transactions
        where Transaction_Date between '2025-11-20' and '2026-01-25'
    ) t on c.CustomerID = t.CustomerID
),

-- -------------------------------------------------------------------------
-- 6. Trend features (2 features)
-- Avg transaction size change across months.
-- -------------------------------------------------------------------------
trends as (
    select
        CustomerID as customer_id,

        -- Avg transaction size Dec vs Nov
        round(
            (sum(case when month(Transaction_Date) = 12
                then Amount_Completed else 0 end)
            / nullif(count(case when month(Transaction_Date) = 12
                then 1 end), 0))
            /
            nullif(
                sum(case when month(Transaction_Date) = 11
                    then Amount_Completed else 0 end)
                / nullif(count(case when month(Transaction_Date) = 11
                    then 1 end), 0)
            , 0),
        4) as dec_to_nov_avg_amount_ratio,

        -- Avg transaction size Jan vs Dec
        round(
            (sum(case when month(Transaction_Date) = 1
                then Amount_Completed else 0 end)
            / nullif(count(case when month(Transaction_Date) = 1
                then 1 end), 0))
            /
            nullif(
                sum(case when month(Transaction_Date) = 12
                    then Amount_Completed else 0 end)
                / nullif(count(case when month(Transaction_Date) = 12
                    then 1 end), 0)
            , 0),
        4) as jan_to_dec_avg_amount_ratio

    from silver.transactions
    where Transaction_Date between '2025-11-20' and '2026-01-25'
    group by CustomerID
),

-- -------------------------------------------------------------------------
-- Final join
-- customer_id and Individual are identifiers, not features.
-- LEFT JOIN from spending_agg retains all customers even if a feature
-- family returns no rows (e.g. no Nov transactions -> ratio is NULL).
-- -------------------------------------------------------------------------
final as (
    select
        -- Identifiers
        s.customer_id,
        d.Individual,

        -- 1. Spending aggregates (7)
        s.total_spend,
        s.transaction_count,
        s.avg_transaction_amount,
        s.median_transaction_amount,
        s.std_transaction_amount,
        s.max_transaction_amount,
        s.min_transaction_amount,

        -- 2. Category shares (19)
        c.grocery_share,
        c.dining_share,
        c.gas_share,
        c.digital_share,
        c.electronics_share,
        c.telecom_share,
        c.retail_share,
        c.healthcare_share,
        c.pets_share,
        c.home_share,
        c.automotive_share,
        c.clothing_share,
        c.entertainment_share,
        c.financial_share,
        c.personal_care_share,
        c.transport_share,
        c.utilities_share,
        c.government_share,
        c.other_share,

        -- 3. Temporal (4)
        t.weekend_share,
        t.avg_transactions_per_week,
        t.dec_to_nov_daily_spend_ratio,
        t.jan_to_dec_daily_spend_ratio,

        -- 4. Merchant behavior (5)
        m.unique_merchants,
        m.top_merchant_share,
        m.repeat_merchant_rate,
        m.repeat_transaction_rate,
        m.avg_visits_per_merchant,

        -- 5. Demographics (18)
        d.Age,
        d.RelationshipYears,
        d.is_male,
        d.is_female,
        d.NumberActiveDDAs,
        d.NumberActiveTimeDeposits,
        d.NumberActiveLoans,
        d.NumberCreditCardAccts,
        d.has_deposit,
        d.has_loan,
        d.has_creditcard,
        d.has_atm,
        d.has_debit,
        d.is_primary,
        d.is_wealth,
        d.is_payroll,
        d.is_pling,
        d.is_able,

        -- 6. Trends (2)
        tr.dec_to_nov_avg_amount_ratio,
        tr.jan_to_dec_avg_amount_ratio

    from spending_agg s
    left join category_shares  c  on s.customer_id = c.customer_id
    left join temporal         t  on s.customer_id = t.customer_id
    left join merchant         m  on s.customer_id = m.customer_id
    left join demographics     d  on s.customer_id = d.customer_id
    left join trends           tr on s.customer_id = tr.customer_id
)

select * from final