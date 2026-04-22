# Project Architecture & Visio Documentation

As part of the enterprise documentation requirement, these diagrams outline the technical flow. They are written in Mermaid.js syntax, which can directly mirror Visio logic. These can be pasted into any markdown reader (like GitHub) to render flowcharts.

## 1. High-Level Enterprise Data Architecture
This represents the macro view of systems.

```mermaid
graph LR
    subgraph "Source Systems"
        A[Claims API] --> |JSON / CSV| D(Landing Zone - Secure Server)
        B[Provider Master DB] --> |Export| D
        C[Member Portal] --> |Delta Loads| D
    end

    subgraph "ETL Processing (IBM DataStage Equivalent)"
        D --> E[Staging Area]
        E --> |Data Cleansing & Validation| F[Transform / Joins]
        F --> |Business Logic / CDC| G[Enterprise Data Warehouse]
    end

    subgraph "Snowflake Data Warehouse"
        G --> H[(Main / Core Schema)]
        H --> I[(Reporting Views)]
    end

    subgraph "Analytics & BI"
        I --> J[Tableau Server]
        J --> K(Executive Dashboards)
        J --> L(Ops Dashboards)
    end
    
    style G fill:#29b6f6,stroke:#01579b,stroke-width:2px;
    style J fill:#ef5350,stroke:#b71c1c,stroke-width:2px;
```

---

## 2. ETL Process Flow (Job Dependency)
This flow represents the logic built into DataStage sequencers.

```mermaid
flowchart TD
    Start((Start Nightly Batch)) --> CheckFiles{Are Source Files Present?}
    CheckFiles -- No --> Alert[Send Alert Email to Data Ops]
    CheckFiles -- Yes --> Job1(Job 1: Extract to Staging)
    
    Job1 --> CheckHealth1{D/Q Check Nulls}
    CheckHealth1 -- Fail thresholds --> Abort(Abort Pipeline)
    CheckHealth1 -- Pass --> Job2(Job 2: Apply Surrogate Keys & Logic)
    
    Job2 --> Fork1{Route Records}
    Fork1 --> |Valid Data| LoadDB[Load to Snowflake Core]
    Fork1 --> |Invalid Formats| ErrorTable[Write to Reject Table]
    
    ErrorTable --> Review(Data Steward Review Queue)
    LoadDB --> Job3(Job 3: Refresh Tableau Extract)
    Job3 --> End((Batch Complete))
```

---

## 3. Claim Lifecycle Entity Relationship (Conceptual Data Model)

This is the Star/Snowflake schema logic used for BI.

```mermaid
erDiagram
    CLAIMS_FACT {
        string claim_id PK
        string member_id FK
        string provider_id FK
        date service_date
        float claim_amount
        float approved_amount
        string claim_status
        int sla_days
    }
    MEMBERS_DIM {
        string member_id PK
        string first_name
        string gender
        int age
        string chronic_condition
    }
    PROVIDERS_DIM {
        string provider_id PK
        string npi_code
        string specialty
        string network_status
    }

    CLAIMS_FACT }o--|| MEMBERS_DIM : "has patient"
    CLAIMS_FACT }o--|| PROVIDERS_DIM : "serviced by"
```
