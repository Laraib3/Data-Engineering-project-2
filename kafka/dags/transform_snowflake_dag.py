from airflow import DAG
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'laraib',
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

with DAG(
    dag_id='transform_snowflake_data',
    default_args=default_args,
    start_date=datetime(2025, 5, 22),
    schedule_interval='@hourly',
    catchup=False
) as dag:

    transform_data = SnowflakeOperator(
        task_id='transform_kafka_events',
        sql='sql/transform_staged_to_tabular.sql',
        snowflake_conn_id='snowflake_conn',
    )
