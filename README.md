# Data Engineering Project 2

This project demonstrates an end-to-end data pipeline using Kafka, Snowflake, and Airflow, orchestrated with Docker. It covers data generation, streaming, ingestion, transformation, and loading into BigQuery.

## Project Structure

```
Data-Engineering-project-2/
│
├── generator/
│   └── mock_generator.py           # Python script to generate mock data for Kafka
│
├── kafka/
│   ├── docker-compose.yml          # Docker Compose file for Kafka, Zookeeper, and Airflow
│   ├── Dockerfile                  # Dockerfile for custom services (if any)
│   ├── requirements.txt            # Python dependencies for Kafka/Airflow
│   └── dags/
│       ├── gcp-credentials.json    # GCP credentials for BigQuery
│       ├── snowflake_to_bigquery_dag.py  # Airflow DAG: Snowflake → BigQuery
│       ├── transform_snowflake_dag.py    # Airflow DAG: Transform Snowflake data
│       └── sql/
│           └── transform_staged_to_tabular.sql # SQL for data transformation
│
├── init_snowflake.sql              # SQL script to initialize Snowflake DB, schema, and tables
├── run_pipeline.sh                 # Main pipeline orchestration script (Linux/Mac)
├── setup_requirements.txt          # Python dependencies for setup
├── snowsql-1.2.31-linux_x86_64.bash# SnowSQL CLI installer (Linux)
├── .env                            # Environment variables (not committed)
└── README.md                       # Project documentation
```

## Pipeline Overview

1. **Mock Data Generation**: `generator/mock_generator.py` produces sample data and sends it to Kafka.
2. **Kafka & Zookeeper**: Managed via Docker Compose (`kafka/docker-compose.yml`).
3. **Kafka Consumer**: (Script not shown) Consumes Kafka messages and loads them into Snowflake.
4. **Snowflake Initialization**: `init_snowflake.sql` sets up the database, schema, and tables.
5. **Airflow Orchestration**: Airflow DAGs in `kafka/dags/` handle data transformation and loading from Snowflake to BigQuery.
6. **BigQuery**: Final destination for processed data (credentials in `gcp-credentials.json`).

## How to Run

1. **Set up Environment Variables**
   - Copy `.env.example` to `.env` and fill in your credentials (Snowflake, GCP, etc.).

2. **Run the Pipeline**
   - On Linux/Mac:
     ```bash
     bash run_pipeline.sh
     ```
   - On Windows, adapt the script or use WSL.

3. **What the Script Does**
   - Sets up Python virtual environment and dependencies
   - Installs SnowSQL CLI
   - Starts Kafka and Zookeeper via Docker
   - Runs the mock data generator and Kafka consumer
   - Initializes Snowflake
   - Starts Airflow and triggers DAGs for ETL

## Requirements
- Docker & Docker Compose
- Python 3.x
- SnowSQL CLI
- Snowflake, GCP (BigQuery) accounts

## Notes
- The `.env` file is required for credentials and configuration.
- The pipeline is orchestrated for Linux/Mac. For Windows, use WSL or adapt the script.
- Airflow DAGs are located in `kafka/dags/`.
- The Kafka consumer script should be present in the root directory as `kafka_consumer_to_snowflake.py` (not shown above).

## Credits
- Developed as part of a Data Engineering learning project.