-- ==============================================================================
-- PROJECT: Healthcare Claims & Member Insights
-- PURPOSE: Snowflake Database, Schema, and Tables Setup DDL
-- ==============================================================================

-- 1. Create Data Warehouse DB and Schemas
CREATE OR REPLACE DATABASE HEALTHCARE_ANALYTICS_DB
    COMMENT = 'Core database for Healthcare Analytics Optum Project';

USE DATABASE HEALTHCARE_ANALYTICS_DB;

CREATE OR REPLACE SCHEMA STAGING
    COMMENT = 'Staging area for raw CSV ingestion';

CREATE OR REPLACE SCHEMA MAIN
    COMMENT = 'Clean, modeled data ready for BI consumption';

CREATE OR REPLACE SCHEMA REPORTING
    COMMENT = 'Views specifically tailored and materialized for Tableau linking';

-- ==============================================================================
-- 2. CREATE STAGING TABLES (RAW INGESTION)
-- ==============================================================================
USE SCHEMA STAGING;

-- (Assuming CSV column mappings directly to Snowflake variants or strings initially, 
-- but for rigor we type cast directly in DDL)

CREATE OR REPLACE TABLE stg_members (
    member_id VARCHAR(50),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    dob DATE,
    gender VARCHAR(10),
    address VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(20),
    plan_id VARCHAR(50),
    chronic_condition_flag VARCHAR(100),
    enrollment_date DATE,
    age INT
);

CREATE OR REPLACE TABLE stg_providers (
    provider_id VARCHAR(50),
    provider_npi VARCHAR(50),
    provider_name VARCHAR(255),
    specialty VARCHAR(150),
    clinic_name VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    network_status VARCHAR(50)
);

CREATE OR REPLACE TABLE stg_claims (
    claim_id VARCHAR(50),
    member_id VARCHAR(50),
    provider_id VARCHAR(50),
    service_date DATE,
    diagnosis_code VARCHAR(50),
    claim_amount FLOAT,
    approved_amount FLOAT,
    claim_status VARCHAR(50),
    rejection_reason VARCHAR(255),
    submission_date DATE,
    processing_date DATE,
    sla_days INT
);

-- Note: In a real environment, we'd use 'COPY INTO' from AWS S3 or Snowflake Stages here.
-- Example: 
-- COPY INTO stg_claims FROM @my_s3_stage/claims.csv FILE_FORMAT = (TYPE = CSV, SKIP_HEADER = 1);

-- ==============================================================================
-- 3. CREATE MAIN ANALYTICS TABLES
-- ==============================================================================
USE SCHEMA MAIN;

-- We migrate data from staging to core in ELT fashion (simulated here)
CREATE OR REPLACE TABLE members CLONE STAGING.stg_members;
CREATE OR REPLACE TABLE providers CLONE STAGING.stg_providers;
CREATE OR REPLACE TABLE claims CLONE STAGING.stg_claims;

-- ==============================================================================
-- 4. CREATE REPORTING VIEWS FOR TABLEAU
-- ==============================================================================
USE SCHEMA REPORTING;

-- View optimized for Tableau Executive Dashboard
CREATE OR REPLACE VIEW vw_executive_summary AS
SELECT 
    c.claim_id,
    c.claim_amount,
    c.approved_amount,
    c.claim_status,
    c.rejection_reason,
    c.service_date,
    m.age,
    m.gender,
    m.state AS member_state,
    m.chronic_condition_flag,
    p.specialty,
    p.network_status
FROM MAIN.claims c
JOIN MAIN.members m ON c.member_id = m.member_id
JOIN MAIN.providers p ON c.provider_id = p.provider_id;

-- View optimized for Operational SLA tracking
CREATE OR REPLACE VIEW vw_operations_sla_tracking AS
SELECT 
    c.claim_id,
    c.provider_id,
    p.provider_name,
    c.claim_status,
    c.sla_days,
    c.submission_date,
    c.processing_date
FROM MAIN.claims c
JOIN MAIN.providers p ON c.provider_id = p.provider_id
WHERE c.sla_days > 0;
