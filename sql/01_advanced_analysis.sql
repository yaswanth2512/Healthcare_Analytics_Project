-- ==============================================================================
-- PROJECT: Healthcare Claims & Member Insights
-- PURPOSE: Advanced Analytical Queries (CTEs, Window Functions, Aggregations)
-- DIALECT: Snowflake SQL
-- ==============================================================================

USE DATABASE HEALTHCARE_ANALYTICS_DB;
USE SCHEMA MAIN;

-- ------------------------------------------------------------------------------
-- 1. Monthly Trend Analysis: Claim Spend & Volume (Window Functions)
-- ------------------------------------------------------------------------------
WITH MonthlyMetrics AS (
    SELECT 
        DATE_TRUNC('month', TO_DATE(service_date, 'YYYY-MM-DD')) AS claim_month,
        COUNT(claim_id) AS total_claims,
        SUM(claim_amount) AS total_claim_amount,
        SUM(approved_amount) AS total_approved_amount
    FROM claims
    GROUP BY 1
)
SELECT 
    claim_month,
    total_claims,
    total_claim_amount,
    -- Calculate Month-over-Month percentage change
    LAG(total_claim_amount) OVER (ORDER BY claim_month) AS prev_month_amount,
    ROUND((total_claim_amount - LAG(total_claim_amount) OVER (ORDER BY claim_month)) / 
          NULLIF(LAG(total_claim_amount) OVER (ORDER BY claim_month), 0) * 100, 2) AS mom_growth_pct
FROM MonthlyMetrics
ORDER BY claim_month DESC;


-- ------------------------------------------------------------------------------
-- 2. Top High-Cost Members (CTEs & Joins)
-- ------------------------------------------------------------------------------
WITH MemberSpend AS (
    SELECT 
        m.member_id,
        m.first_name || ' ' || m.last_name AS member_name,
        m.age,
        m.chronic_condition_flag,
        COUNT(c.claim_id) AS claim_count,
        SUM(c.claim_amount) AS total_spend
    FROM members m
    JOIN claims c ON m.member_id = c.member_id
    WHERE c.claim_status = 'Approved'
    GROUP BY 1, 2, 3, 4
)
SELECT * 
FROM MemberSpend
-- Top 1% threshold simulation
WHERE total_spend > (SELECT PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY total_spend) FROM MemberSpend)
ORDER BY total_spend DESC;


-- ------------------------------------------------------------------------------
-- 3. Claim Rejection Reason Breakdown & Percentages
-- ------------------------------------------------------------------------------
SELECT 
    rejection_reason,
    COUNT(*) AS rejection_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage_of_total_rejections
FROM claims
WHERE claim_status = 'Denied'
GROUP BY 1
ORDER BY rejection_count DESC;


-- ------------------------------------------------------------------------------
-- 4. Provider Performance Ranking based on Avg Claim SLA Delay
-- ------------------------------------------------------------------------------
WITH ProviderSLA AS (
    SELECT 
        p.provider_id,
        p.provider_name,
        p.specialty,
        COUNT(c.claim_id) AS total_claims_processed,
        AVG(DATEDIFF('day', TO_DATE(c.submission_date, 'YYYY-MM-DD'), TO_DATE(c.processing_date, 'YYYY-MM-DD'))) AS avg_turnaround_days
    FROM providers p
    JOIN claims c ON p.provider_id = c.provider_id
    GROUP BY 1, 2, 3
)
SELECT 
    provider_id,
    provider_name,
    specialty,
    total_claims_processed,
    ROUND(avg_turnaround_days, 1) AS avg_turnaround_days,
    DENSE_RANK() OVER (ORDER BY avg_turnaround_days DESC) as sla_delay_rank
FROM ProviderSLA
WHERE total_claims_processed > 50
ORDER BY sla_delay_rank;


-- ------------------------------------------------------------------------------
-- 5. Readmission Risk Indicators (Complex Self-Join / Lead)
-- ------------------------------------------------------------------------------
-- Identifies members who had multiple visits within 30 days
WITH PatientVisits AS (
    SELECT 
        member_id,
        appointment_date AS visit_date,
        LEAD(appointment_date) OVER (PARTITION BY member_id ORDER BY appointment_date) AS next_visit_date,
        appointment_type
    FROM appointments
)
SELECT 
    m.chronic_condition_flag,
    COUNT(DISTINCT v.member_id) AS count_readmitted_members,
    ROUND(AVG(DATEDIFF('day', TO_DATE(v.visit_date, 'YYYY-MM-DD'), TO_DATE(v.next_visit_date, 'YYYY-MM-DD'))), 1) AS avg_days_to_readmit
FROM PatientVisits v
JOIN members m ON v.member_id = m.member_id
WHERE DATEDIFF('day', TO_DATE(v.visit_date, 'YYYY-MM-DD'), TO_DATE(v.next_visit_date, 'YYYY-MM-DD')) <= 30
GROUP BY 1
ORDER BY count_readmitted_members DESC;
