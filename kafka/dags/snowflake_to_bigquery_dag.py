from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import json
import os
import snowflake.connector
from snowflake.connector.errors import DatabaseError, ProgrammingError
from google.cloud import bigquery
from google.oauth2 import service_account
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set OCSP environment variables for Snowflake
os.environ["SF_OCSP_FAIL_OPEN"] = "true"
os.environ["SF_OCSP_RESPONSE_CACHE_SERVER_ENABLED"] = "false"

# Create temp directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(BASE_DIR, 'temp')
os.makedirs(TEMP_DIR, exist_ok=True)

# Snowflake configuration from .env
SNOWFLAKE_CONFIG = {
    'user': os.getenv('SNOWFLAKE_USER'),
    'password': os.getenv('SNOWFLAKE_PASSWORD'),
    'account': os.getenv('SNOWFLAKE_ACCOUNT'),
    'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE'),
    'database': os.getenv('SNOWFLAKE_DATABASE'),
    'schema': os.getenv('SNOWFLAKE_SCHEMA'),
    'insecure_mode': True,
    'ocsp_fail_open': True,
    'validate_default_parameters': True,
    'client_session_keep_alive': True,
    'client_session_keep_alive_heartbeat_frequency': 3600
}

# BigQuery config from .env
BIGQUERY_PROJECT = os.getenv("GCP_PROJECT_ID")
BIGQUERY_DATASET = os.getenv("BIGQUERY_DATASET")
BIGQUERY_TABLE = os.getenv("BIGQUERY_TABLE")
GCP_CREDENTIALS_PATH = os.getenv("GCP_CREDENTIALS_PATH")

# ------------------ Snowflake Extraction ------------------ #
def extract_from_snowflake():
    conn = cursor = None
    try:
        conn = snowflake.connector.connect(**SNOWFLAKE_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT RAW_DATA FROM KAFKA_EVENTS")
        rows = cursor.fetchall()
        
        output_file = Path(TEMP_DIR) / 'raw_data.json'
        with open(output_file, 'w') as f:
            for row in rows:
                if row and row[0]:
                    try:
                        data = json.loads(str(row[0]))
                        json.dump(data, f)
                        f.write('\n')
                    except json.JSONDecodeError:
                        continue

    except Exception as e:
        logger.error(f"Snowflake extract error: {str(e)}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ------------------ Data Transformation ------------------ #
def transform_data():
    input_path = os.path.join(TEMP_DIR, 'raw_data.json')
    output_path = os.path.join(TEMP_DIR, 'transformed_data.json')

    with open(input_path, 'r') as infile, open(output_path, 'w') as outfile:
        for line in infile:
            try:
                data = json.loads(line.strip())
                transformed = {
                    "name": data.get("user", {}).get("name", ""),
                    "email": data.get("user", {}).get("email", ""),
                    "country": data.get("user", {}).get("location", {}).get("country", ""),
                    "timestamp": data.get("event_timestamp", ""),
                    "order_id": data.get("order", {}).get("order_id", ""),
                    "order_status": data.get("order", {}).get("status", ""),
                    "total_amount": data.get("order", {}).get("total_amount", 0),
                    "payment_method": data.get("order", {}).get("payment_method", ""),
                    "device": data.get("session", {}).get("device", ""),
                    "os": data.get("session", {}).get("os", "")
                }
                outfile.write(json.dumps(transformed) + '\n')
            except Exception:
                continue

# ------------------ Load to BigQuery ------------------ #
def load_into_bigquery():
    if not os.path.exists(GCP_CREDENTIALS_PATH):
        raise FileNotFoundError(f"Credentials file not found: {GCP_CREDENTIALS_PATH}")

    credentials = service_account.Credentials.from_service_account_file(
        GCP_CREDENTIALS_PATH,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )

    client = bigquery.Client(credentials=credentials, project=BIGQUERY_PROJECT)
    table_id = f"{BIGQUERY_PROJECT}.{BIGQUERY_DATASET}.{BIGQUERY_TABLE}"

    schema = [
        bigquery.SchemaField("name", "STRING"),
        bigquery.SchemaField("email", "STRING"),
        bigquery.SchemaField("country", "STRING"),
        bigquery.SchemaField("timestamp", "TIMESTAMP"),
        bigquery.SchemaField("order_id", "STRING"),
        bigquery.SchemaField("order_status", "STRING"),
        bigquery.SchemaField("total_amount", "FLOAT"),
        bigquery.SchemaField("payment_method", "STRING"),
        bigquery.SchemaField("device", "STRING"),
        bigquery.SchemaField("os", "STRING")
    ]

    try:
        client.get_table(table_id)
    except Exception:
        table = bigquery.Table(table_id, schema=schema)
        client.create_table(table)

    with open(os.path.join(TEMP_DIR, "transformed_data.json"), "rb") as source_file:
        job = client.load_table_from_file(
            source_file,
            table_id,
            job_config=bigquery.LoadJobConfig(
                source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
                schema=schema,
                write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
                ignore_unknown_values=True,
            ),
        )
        job.result()

# ------------------ DAG Definition ------------------ #
default_args = {
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
}

with DAG(
    dag_id='snowflake_to_bigquery',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    description="Extract Snowflake data, transform, and load into BigQuery",
    tags=['snowflake', 'bigquery']
) as dag:

    extract = PythonOperator(
        task_id='extract_from_snowflake',
        python_callable=extract_from_snowflake
    )

    transform = PythonOperator(
        task_id='transform_data',
        python_callable=transform_data
    )

    load = PythonOperator(
        task_id='load_into_bigquery',
        python_callable=load_into_bigquery
    )

    extract >> transform >> load
