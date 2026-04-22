-- ==============================================================================
-- PROJECT: Healthcare Claims & Member Insights
-- PURPOSE: Data Quality Validation and Profiling Queries
-- DIALECT: Snowflake SQL
-- ==============================================================================

USE DATABASE HEALTHCARE_ANALYTICS_DB;
USE SCHEMA MAIN;

-- ------------------------------------------------------------------------------
-- 1. Identify Orphan Records (Referential Integrity Check)
-- Claims referencing a Member ID not in the Member table
-- ------------------------------------------------------------------------------
SELECT 
    'Claims without valid Member' AS quality_issue_type,
    COUNT(*) AS error_count
FROM claims c
LEFT JOIN members m ON c.member_id = m.member_id
WHERE m.member_id IS NULL

UNION ALL

-- Claims referencing a Provider ID not in the Provider table
SELECT 
    'Claims without valid Provider' AS quality_issue_type,
    COUNT(*) AS error_count
FROM claims c
LEFT JOIN providers p ON c.provider_id = p.provider_id
WHERE p.provider_id IS NULL;


-- ------------------------------------------------------------------------------
-- 2. Duplicate Detection
-- Find exact duplicates in members table
-- ------------------------------------------------------------------------------
SELECT 
    member_id,
    first_name,
    last_name,
    COUNT(*) AS occurances
FROM members
GROUP BY member_id, first_name, last_name
HAVING COUNT(*) > 1;

-- Find potential duplicate claims (same member, same provider, same date, same amount)
SELECT 
    member_id,
    provider_id,
    service_date,
    claim_amount,
    COUNT(*) AS duplicate_claims_count
FROM claims
GROUP BY 1, 2, 3, 4
HAVING COUNT(*) > 1;


-- ------------------------------------------------------------------------------
-- 3. Completeness & Null value checks
-- Calculate percentage of missing values per critical column
-- ------------------------------------------------------------------------------
SELECT 
    'Claims: Missing Diagnosis Code' AS metric_name,
    SUM(IFF(diagnosis_code IS NULL OR diagnosis_code = '', 1, 0)) AS missing_count,
    COUNT(*) AS total_count,
    ROUND(SUM(IFF(diagnosis_code IS NULL OR diagnosis_code = '', 1, 0)) / COUNT(*) * 100, 2) AS missing_percent
FROM claims

UNION ALL

SELECT 
    'Members: Missing Zip Code' AS metric_name,
    SUM(IFF(zip_code IS NULL OR zip_code = '', 1, 0)) AS missing_count,
    COUNT(*) AS total_count,
    ROUND(SUM(IFF(zip_code IS NULL OR zip_code = '', 1, 0)) / COUNT(*) * 100, 2) AS missing_percent
FROM members;


-- ------------------------------------------------------------------------------
-- 4. Logical Validation Checks
-- Ensure approved amounts are never greater than submitted claim amounts
-- Ensure Processed dates happen AFTER formulation/submission dates
-- ------------------------------------------------------------------------------
SELECT 
    claim_id,
    claim_amount,
    approved_amount,
    'Approved amount exceeds requested' AS error_description
FROM claims
WHERE approved_amount > claim_amount;

SELECT 
    claim_id,
    service_date,
    submission_date,
    processing_date,
    'Invalid Timeline Sequence' AS error_description
FROM claims
WHERE TO_DATE(submission_date, 'YYYY-MM-DD') < TO_DATE(service_date, 'YYYY-MM-DD')
   OR TO_DATE(processing_date, 'YYYY-MM-DD') < TO_DATE(submission_date, 'YYYY-MM-DD');
