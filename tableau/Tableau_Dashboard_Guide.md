# Tableau Dashboard Architecture & Setup Guide

This guide details the schema and precise steps to recreate the interactive Analytics Dashboards using Tableau Desktop, matching Optum UI/UX expectations.

## 1. Connecting to Snowflake Data Source
1. Open Tableau Desktop.
2. Select **Connect to Server** -> **Snowflake**.
3. Input server endpoint, Role `TABLEAU_SERVICE_ROLE`, Database `HEALTHCARE_ANALYTICS_DB`, Warehouse `TABLEAU_REPORTING_WH`.
4. Drag `vw_executive_summary` into the data modeling canvas.

---

## 2. Dashboard 1: Executive Overview (The "Wow" Factor)

**Target Audience:** VP Operations, Medical Directors
**Layout Template:** Dark Mode / High Contrast Modern (Dark Blue Backgrounds #0d1b2a, crisp white/cyan text #00b4d8).

### KPIs (Top Banner)
*   **Total Claims Processed:** `COUNT(claim_id)` (Formatted as #,##0K). Apply color logic (Green if MoM growth > 0).
*   **Total Claims Paid:** `SUM(approved_amount)` (Formatted as Currency $M).
*   **Rejection Rate:** Calculated Field: `SUM(IF [claim_status]='Denied' THEN 1 ELSE 0 END) / COUNT([claim_id])`. Format as %.

### Visualizations:
*   **Claim Spend over Time (Line Chart):** Columns: `MONTH(service_date)`, Rows: `SUM(approved_amount)`. Dual axis with `COUNT(claim_id)`.
*   **Spend by Region/State (Filled Map):** Geographic role `member_state`. Color gradient based on High Cost. Tooltip reveals Top 3 highest costing claims in that state.
*   **Claim Status Breakdown (Donut Chart):** Pie chart showing Approved, Denied, Pending. Dual axis to hollow out center for a donut effect.

---

## 3. Dashboard 2: Provider & Operations SLA

**Target Audience:** Claims Processing Managers

### Interactive Filters:
*   `specialty` drop-down.
*   `network_status` toggle.

### Visualizations:
*   **Provider Turnaround Time Ranking (Bar Chart):** Columns: `avg(sla_days)`, Rows: `provider_name` (Sorted Descending). Use red color for bars exceeding standard SLA (> 7 days).
*   **Rejection Reasons Pareto Chart:** Columns: `rejection_reason`. Rows: `COUNT(claim_id)`. Include dual-axis cumulative curve line. Identifies critical bottlenecks like "Missing Prior Auth".
*   **SLA Distribution (Box and Whisker Plot):** Visualize the spread of SLA days across different Clinic locations to find process outliers.

---

## 4. Dashboard 3: Population Health Insights

**Target Audience:** Clinical Data Analysts

### Visualizations:
*   **Chronic Condition Cost Impact (Treemap):** Size based on `COUNT(member_id)`. Color intensity based on `SUM(claim_amount)`. 'Diabetes' and 'Hypertension' will visually pop as the largest boxes.
*   **Demographic Readmission Heatmap:** Rows: Age Groups (Calculated Field using Age Bins), Columns: Gender. Color indicates Average Spend per member.
*   **Medication vs Claim Cost Scatterplot:** (Requires blending Pharmacy view). X-axis: Pharmacy Cost. Y-axis: Medical Claim Cost. Include a trendline to evaluate if high pharma spend lowers overall medical spend (preventative care theory).

---

## 5. Advanced Interactive Capabilities to Implement

*   **Parameter Swapping:** Include a parameter `Select Metric: [Spend | Volume]`. Use a calculated field so users can dynamically swap what the bar charts represent.
*   **Dashboard Actions (Drill-Down):** Set up a Filter Action on the State Map. Clicking "Texas" will actively filter the 'Provider Bar Chart' and 'Provider Pareto Chart' to only show Texas providers.
*   **Custom Tooltips:** Edit the marks tooltip manually: 
    * *Example:* "Provider `<provider_name>` has cost our plan `<SUM(claim_amount)>` year-to-date across `<COUNT(claim_id)>` claims."

---

## 6. Performance Optimization Notes
*   Use **Extracts** (.hyper files) if underlying Snowflake data becomes larger than 10M rows to ensure sub-second dashboard rendering.
*   Hide all unused fields in the data pane before publishing to Tableau Server.
*   Leverage Custom SQL only at the Database View level, never inside Tableau’s SQL interface, to offload processing to Snowflake.
