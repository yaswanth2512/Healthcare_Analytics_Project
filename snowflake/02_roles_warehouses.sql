-- ==============================================================================
-- PROJECT: Healthcare Claims & Member Insights
-- PURPOSE: Snowflake Warehouses, Roles, and Access Management
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 1. Create Virtual Warehouses
-- ------------------------------------------------------------------------------
-- Dedicated warehouse for heavy ETL loads (IBM DataStage service)
CREATE OR REPLACE WAREHOUSE ETL_WH 
    WITH WAREHOUSE_SIZE = 'LARGE' 
    AUTO_SUSPEND = 60 
    AUTO_RESUME = TRUE 
    INITIALLY_SUSPENDED = TRUE
    COMMENT = 'Warehouse for heavy batch processing and ELT transformations';

-- Dedicated warehouse for Tableau Reporting concurrency
CREATE OR REPLACE WAREHOUSE TABLEAU_REPORTING_WH 
    WITH WAREHOUSE_SIZE = 'MEDIUM' 
    MAX_CLUSTER_COUNT = 3 
    MIN_CLUSTER_COUNT = 1 
    SCALING_POLICY = 'STANDARD'
    AUTO_SUSPEND = 120 
    AUTO_RESUME = TRUE 
    COMMENT = 'Multi-cluster scalable warehouse for dynamic BI dashboards';

-- ------------------------------------------------------------------------------
-- 2. Create Functional Roles
-- ------------------------------------------------------------------------------
CREATE OR REPLACE ROLE ETL_SERVICE_ROLE;
CREATE OR REPLACE ROLE DATA_ANALYST_ROLE;
CREATE OR REPLACE ROLE TABLEAU_SERVICE_ROLE;

-- Hierarchy setup
GRANT ROLE ETL_SERVICE_ROLE TO ROLE SYSADMIN;
GRANT ROLE DATA_ANALYST_ROLE TO ROLE SYSADMIN;
GRANT ROLE TABLEAU_SERVICE_ROLE TO ROLE SYSADMIN;

-- ------------------------------------------------------------------------------
-- 3. Apply Grants and Privilege Assignments
-- ------------------------------------------------------------------------------

-- ETL Role Needs Full access to Staging and Core Schemas
GRANT USAGE ON WAREHOUSE ETL_WH TO ROLE ETL_SERVICE_ROLE;
GRANT ALL PRIVILEGES ON DATABASE HEALTHCARE_ANALYTICS_DB TO ROLE ETL_SERVICE_ROLE;
GRANT ALL PRIVILEGES ON ALL SCHEMAS IN DATABASE HEALTHCARE_ANALYTICS_DB TO ROLE ETL_SERVICE_ROLE;

-- Analyst Role Needs Read/Write in Analytics but only Read in Staging
GRANT USAGE ON WAREHOUSE TABLEAU_REPORTING_WH TO ROLE DATA_ANALYST_ROLE;
GRANT USAGE ON DATABASE HEALTHCARE_ANALYTICS_DB TO ROLE DATA_ANALYST_ROLE;
GRANT USAGE ON SCHEMA HEALTHCARE_ANALYTICS_DB.MAIN TO ROLE DATA_ANALYST_ROLE;
GRANT SELECT ON ALL TABLES IN SCHEMA HEALTHCARE_ANALYTICS_DB.MAIN TO ROLE DATA_ANALYST_ROLE;

-- Tableau Role Only needs SELECT on Reporting views
GRANT USAGE ON WAREHOUSE TABLEAU_REPORTING_WH TO ROLE TABLEAU_SERVICE_ROLE;
GRANT USAGE ON DATABASE HEALTHCARE_ANALYTICS_DB TO ROLE TABLEAU_SERVICE_ROLE;
GRANT USAGE ON SCHEMA HEALTHCARE_ANALYTICS_DB.REPORTING TO ROLE TABLEAU_SERVICE_ROLE;
GRANT SELECT ON ALL VIEWS IN SCHEMA HEALTHCARE_ANALYTICS_DB.REPORTING TO ROLE TABLEAU_SERVICE_ROLE;

-- Ensure future views get the grant automatically
GRANT SELECT ON FUTURE VIEWS IN SCHEMA HEALTHCARE_ANALYTICS_DB.REPORTING TO ROLE TABLEAU_SERVICE_ROLE;
