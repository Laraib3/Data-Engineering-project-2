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
- The Kafka consumer script should be present in the root directory as `kafka_consumer_to_snowflake.py`. This script now loads all Kafka and Snowflake configuration from environment variables defined in your `.env` file, making it secure and easy to configure for different environments.

## .env File Structure

Create a `.env` file in the project root with the following variables:

```ini
# Snowflake configuration
SNOWFLAKE_USER=<your-snowflake-username>
SNOWFLAKE_PASSWORD=<your-snowflake-password>
SNOWFLAKE_ACCOUNT=<your-snowflake-account>
SNOWFLAKE_WAREHOUSE=<your-snowflake-warehouse>
SNOWFLAKE_DATABASE=<your-snowflake-database>
SNOWFLAKE_SCHEMA=<your-snowflake-schema>

# Kafka configuration
KAFKA_BROKER=<your-kafka-broker-host:port>
TOPIC_NAME=<your-kafka-topic>

# Google Cloud / BigQuery configuration
GCP_PROJECT_ID=<your-gcp-project-id>
BIGQUERY_DATASET=<your-bigquery-dataset>
BIGQUERY_TABLE=<your-bigquery-table>
GCP_CREDENTIALS_PATH=<absolute/path/to/gcp-credentials.json>

# Airflow Snowflake Connection (used in DAG as `snowflake_conn`)
AIRFLOW_CONN_SNOWFLAKE_CONN=snowflake://<user name>:<password>@<account>/<schema>/<database>?warehouse=<warehouse>

```

- Replace all placeholder values with your actual credentials and configuration.
- The `.env` file is required for the pipeline to run successfully.
- **Never commit your `.env` file to source control.**

## GCP Credentials JSON Structure

This project requires a `gcp-credentials.json` file for authenticating with Google Cloud Platform (GCP) services such as BigQuery. **Do not commit your actual credentials to version control.**

### Example Structure

```json
{
  "type": "service_account",
  "project_id": "<your-gcp-project-id>",
  "private_key_id": "<your-private-key-id>",
  "private_key": "-----BEGIN PRIVATE KEY-----\n<your-private-key>\n-----END PRIVATE KEY-----\n",
  "client_email": "<your-service-account-email>",
  "client_id": "<your-client-id>",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/<your-service-account-email>",
  "universe_domain": "googleapis.com"
}
```

- Replace all placeholder values (e.g., `<your-gcp-project-id>`, `<your-private-key>`) with your actual GCP service account details.
- This file is typically generated and downloaded from the Google Cloud Console when creating a service account.

**Security Note:**
- Never commit your real `gcp-credentials.json` to source control.
- Add `gcp-credentials.json` to your `.gitignore` file to prevent accidental commits.

## Airflow Snowflake Connection Structure

To connect Airflow to Snowflake (used in DAGs as `snowflake_conn`), configure a connection in the Airflow UI or via environment variables with the following fields:

| Field         | Example Value              | Description                       |
|---------------|---------------------------|-----------------------------------|
| Conn Id       | snowflake_conn            | Connection ID used in DAGs        |
| Conn Type     | Snowflake                 | Select 'Snowflake'                |
| Host          | <your-snowflake-account>  | Snowflake account identifier      |
| Schema        | <your-snowflake-schema>   | Default schema                    |
| Login         | <your-snowflake-username> | Snowflake username                |
| Password      | <your-snowflake-password> | Snowflake password                |
| Extra         | {"account": "<your-snowflake-account>", "warehouse": "<your-snowflake-warehouse>", "database": "<your-snowflake-database>"} | JSON for additional params |

**Example `Extra` field:**
```json
{
  "account": "<your-snowflake-account>",
  "warehouse": "<your-snowflake-warehouse>",
  "database": "<your-snowflake-database>"
}
```

- You can set this connection in the Airflow UI (Admin > Connections) or by using environment variables (see Airflow docs for details).
- The values should match those in your `.env` file for consistency.

## SnowSQL CLI Connection Configuration

To use the SnowSQL CLI, you need to create a configuration file at `~/.snowsql/config` with your Snowflake connection details. Example:

```ini
[connections.my_conn]
accountname = <your-snowflake-account>
username = <your-snowflake-username>
password = <your-snowflake-password>
warehousename = <your-snowflake-warehouse>
dbname = <your-snowflake-database>
schemaname = <your-snowflake-schema>
rolename = <your-snowflake-role>
```

- Replace all placeholder values with your actual Snowflake credentials.
- This configuration allows you to use the `snowsql` command-line tool for database operations.
- The connection name (`my_conn`) can be referenced in your scripts or commands.

## SnowSQL CLI Installer

The SnowSQL installer script (`snowsql-1.2.31-linux_x86_64.bash`) should **not** be added to your git repository. Add it to your `.gitignore` to prevent accidental commits.

### How to Download and Install SnowSQL

Run the following commands to download and install SnowSQL:

```bash
curl -O https://sfc-repo.snowflakecomputing.com/snowsql/bootstrap/1.2/linux_x86_64/snowsql-1.2.31-linux_x86_64.bash
bash snowsql-1.2.31-linux_x86_64.bash
```

- This will download the installer and run it to set up the SnowSQL CLI.
- After installation, ensure that the SnowSQL binary is in your `PATH` as described above.
- The installer script is large and system-specific, so it should not be tracked in version control.

## Credits
- Developed as part of a Data Engineering learning project.