# IBM DataStage / ETL Pipeline Design Specification

As an Optum Data Analyst / Architect, understanding and documenting the ETL flow is critical. While raw DataStage project `.isx` or `.dsx` files cannot be exported here without a DataStage server, this document provides the comprehensive **Enterprise ETL Design Architecture** that mirrors a DataStage implementation.

## 1. ETL Pipeline Overview
**Objective**: Ingest daily external healthcare API drops (simulated as CSVs), clean the data, validate it against master reference data, perform transformations, and load it into Snowflake Data Warehouse for BI consumption.

**Tool Equivalent**: IBM InfoSphere DataStage (Parallel Jobs)

---

## 2. Job Flow Architecture

### Job 1: `jb_Extract_Landing_to_Staging`
*   **Stage 1 (Sequential File)**: Reads raw `claims.csv`, `members.csv`, `providers.csv`.
*   **Stage 2 (Transformer)**:
    *   Adds audit columns: `ETL_LOAD_TIMESTAMP`, `JOB_RUN_ID`.
    *   Trims whitespaces from string columns (e.g., `Trim(city)`).
    *   Converts date strings to proper timestamp formats.
*   **Stage 3 (Snowflake Connector - Staging)**: Uses Bulk Load / COPY INTO to load into `HEALTHCARE_ANALYTICS_DB.STAGING.stg_claims`, etc.

### Job 2: `jb_Transform_Data_Quality_Check`
*   **Stage 1 (Snowflake Connector)**: Reads from Staging tables in parallel.
*   **Stage 2 (Lookup)**:
    *   Validates `provider_id` against the Provider Master Reference table.
    *   Rejects claims with orphan providers.
*   **Stage 3 (Filter / Transformer)**:
    *   Routes invalid records (Null members, ages < 0) to a `Reject_Log_File`.
    *   Applies business rules: Calculate `SLA_Days = DateDiff(processing_date, submission_date)`.
*   **Stage 4 (Snowflake Connector - Core)**: Inserts validated data into `HEALTHCARE_ANALYTICS_DB.MAIN` schema.

---

## 3. Advanced DataStage Concepts Utilized

### Incremental Processing (CDC)
*   Instead of Full Loads, the pipeline uses **Change Data Capture**.
*   The pipeline relies on `processing_date` and a high-water mark sequence stored in an ETL control table. 
*   **DataStage Logic**: Compare incoming API data against existing Snowflake data using Hash Keys (Surrogate Keys). Insert new rows; Update changed rows (SCD Type 2 for Members, SCD Type 1 for Claims).

### Error Handling & Reject Links
*   In DataStage Transformers, all reject conditions are captured via **Reject Links**.
*   Any claim hitting failure rules (e.g., `claim_amount < 0`) is routed to an Exception Schema for manual data steward review, ensuring the main pipeline never crashes.

### Restartability & Logging
*   **Sequence Job (Job Sequencer)**: Orchestrates the dependencies. 
*   If `jb_Transform_Data_Quality_Check` fails, checkpoints are utilized. Restarting the sequencer resumes exactly at the failed stage.
*   **Audit Logging**: Every job execution logs `rowCount_extracted`, `rowCount_rejected`, and `rowCount_loaded` to a centralized SQL log table.

---

## 4. Parameter Sets Configuration
Standard DataStage development requires abstracting environments:
| Parameter | DEV Value | PROD Value |
| :--- | :--- | :--- |
| `$DB_SNOW_HOST` | dev-xy1234.snowflakecomputing.com | prod-xy9999.snowflakecomputing.com |
| `$DB_USER` | SVC_ETL_DEV | SVC_ETL_PROD |
| `$FILE_LANDING_DIR` | `/app/optum/data/dev/inbound` | `/app/optum/data/prod/inbound` |

---

*Note: For actual code execution in the context of this portfolio project, the python script `data_cleansing_validation.py` conceptually simulates the validations performed by DataStage.*
