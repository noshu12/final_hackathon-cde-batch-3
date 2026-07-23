# 🛰️ IoT Device Telemetry & Analytics Hub (End-to-End Data Pipeline)

An enterprise-grade, real-time data engineering and analytics pipeline built to ingest, migrate, transform, and visualize streaming telemetry data from on-premise IoT sensors to a modern cloud data warehouse. This project implements a modern data stack (MDS) utilizing **AWS (CDK, IoT, MSK, EC2)**, **Snowflake**, **dbt (Data Build Tool)**, and **Streamlit**.

---

## 🏛️ End-to-End Architecture Diagram

The project is divided into two major phases as per enterprise architecture standards:

### Phase 1: IoT Ingestion & On-Premise Simulation
```text
[ IoT Sensors ] 
      │ (MQTT via AWS IoT Device Simulator)
      ▼
[ AWS IoT Core ] (MQTT Broker & Rules)
      │
      ▼
[ Apache Kafka MSK ] (iot-events topic)
      ├──► [ Kafka S3 Sink Connector ] ──► [ Amazon S3 Backup Bucket ]
      │
      ▼
[ Kafka Connect (JDBC Sink) ]
      │
      ▼
[ PostgreSQL on EC2 ] (Private Subnet - On-Premise Simulation)
  (Managed via Bastion Host & AWS SSM Session Manager)
```

### Phase 2: Cloud CDC Migration, Processing & Analytics
```text
[ PostgreSQL EC2 (WAL Enabled) ]
      │ (CDC via Debezium Connector)
      ▼
[ Apache Kafka MSK ] (cdc.public.iot_events topic)
      │ (Snowflake Kafka Connector)
      ▼
[ Snowflake Bronze Layer ] (`RAW.RAW_IOT_EVENTS`)
      │
      ├──► [ dbt Silver Model ] (`CLEAN.IOT_VALIDATED`) - Cleaning & Validation
      │          │
      │          ▼
      │    [ dbt Gold Model ] (`ANALYTICS.DEVICE_DAILY`) - Incremental Daily Aggregates
      │          │
      │          ▼
      │    [ Streamlit Dashboard ] (Interactive UI & Real-Time Metrics)
      │
      └──► [ AWS Timestream ] ──► [ Grafana ] (Bonus Time-Series Monitoring)
```

---

## 📐 Tech Stack & Components Mapping

| Pipeline Layer | Technologies / Services Used | Role in Project |
| :--- | :--- | :--- |
| **Infrastructure as Code** | Python AWS CDK (`app.py`, `cdk.json`) | Provisioned AWS VPC, Subnets, MSK, and S3 resources. |
| **IoT Ingestion (Phase 1)** | AWS IoT Device Simulator, IoT Core, MQTT | Simulated 5+ parallel IoT devices streaming GPS & telemetry [cite: 1]. |
| **Stream Delivery & Sink** | Apache Kafka (AWS MSK), Kafka Connect JDBC | Handled real-time messaging and wrote streaming payloads to PostgreSQL. |
| **On-Premise Simulation** | PostgreSQL on EC2 (Private Subnet) | Acted as the core transactional database with Write-Ahead Logging (WAL) enabled. |
| **CDC Migration (Phase 2)** | Debezium CDC via Kafka Connect Source | Captured real-time database changes (INSERT, UPDATE, DELETE) without batch lag. |
| **Cloud Data Warehouse** | Snowflake (Bronze, Silver, Gold Schemas) | Cloud repository storing raw CDC streams and structured analytical tables. |
| **Transformations** | dbt-snowflake (Jinja SQL models) | Transformed raw payloads into validated silver and aggregated gold models. |
| **Visualization & BI** | Python Streamlit (`dashboard.py`) | Served live KPI metrics, event distribution charts, and geolocation feeds. |

---

## 📂 Project File Structure

```text
final_hackathon-cde-batch-3/
│
├── app.py                      # AWS CDK Python infrastructure orchestration script
├── cdk.json                    # CDK project configuration file
├── dashboard.py                # Main Streamlit application for real-time analytics UI
├── iot_simulator.py            # Script for generating virtual IoT device telemetry feeds
├── producer.py / producer.js   # Event producers for data streaming pipelines
├── requirements.txt            # Python dependencies for the project
│
├── hackathon_transform/        # Root directory for the dbt transformation project
│   ├── dbt_project.yml         # dbt project configuration and database profiles
│   └── models/                 
│       ├── schema.yml          # Column descriptions, documentation, and data quality tests
│       └── transform/
│           ├── iot_validated.sql # Silver layer model (cleans, validates nulls, parses timestamps)
│           └── device_daily.sql  # Gold layer incremental model (computes daily device metrics)
│
└── README.md                   # Comprehensive project documentation
```

---

## 🛠️ Step-by-Step Implementation & Problem Solving

### 1. Infrastructure & Ingestion Setup (Phase 1)
* **Challenge:** Simulating a live enterprise edge network streaming high-frequency IoT geolocation payloads securely.
* **Solution:** Provisioned AWS cloud infrastructure via CDK, utilizing an MQTT-based simulator routing messages through AWS IoT Core into Apache Kafka (MSK). A JDBC Sink connector safely ingested these streams into a private PostgreSQL EC2 instance configured with Systems Manager (SSM) access.

### 2. Real-Time CDC Migration & Data Warehousing (Phase 2)
* **Challenge:** Moving data from PostgreSQL to Snowflake efficiently without heavy batch processing overhead or data loss.
* **Solution:** Enabled logical replication (WAL) on PostgreSQL and deployed **Debezium CDC** via Kafka Connect. Change data capture events (`cdc.public.iot_events`) were piped directly into Snowflake's Bronze layer (`RAW.RAW_IOT_EVENTS`) using Snowflake connectors.

### 3. Modular Transformations with dbt
* **Challenge:** Normalizing raw unstructured JSON event payloads into structured analytics-ready schemas while managing compute costs.
* **Solution:** 
  * Created the **Silver Model (`iot_validated.sql`)** to filter nulls, format timestamps, and standardize attributes.
  * Designed an **Incremental Gold Model (`device_daily.sql`)** utilizing composite keys (`device_id`, `event_date`) to ensure only new records are processed during routine updates. Full refreshes (`dbt run --full-refresh`) manage historical resets seamlessly.

### 4. Interactive Visualization via Streamlit
* **Challenge:** Delivering low-latency interactive monitoring dashboards connected directly to Snowflake's cloud storage.
* **Solution:** Built `dashboard.py` featuring dynamic KPI cards (`Active Devices`, `Total Events`, `Avg Latitude`, `Avg Longitude`), native bar charts (`st.bar_chart`) for event distribution per device, and auto-refresh mechanisms configured for live operation.

---

## 🚀 How to Run the Project Locally

### Prerequisites
* Python 3.8+ installed
* Snowflake account credentials with access to `HACKATHON_IOT` database
* dbt-snowflake adapter configured

### Step 1: Clone the Repository
```bash
git clone https://github.com/noshu12/final_hackathon-cde-batch-3.git
cd final_hackathon-cde-batch-3
```

### Step 2: Run dbt Transformations
Navigate into the dbt transformation directory and execute the build pipeline:
```bash
cd hackathon_transform
dbt run --full-refresh
```

### Step 3: Launch the Streamlit Dashboard
Return to the project root directory and run the dashboard application:
```bash
cd ..
streamlit run dashboard.py
```
