#!/bin/bash

# Exit on error
set -e
python3 -m venv venv
# Load environment variables from .env
set -a
source .env
set +a

echo "Activating virtual environment..."
source venv/bin/activate

echo "Updating Python dependencies..."
pip install --upgrade pip setuptools wheel --only-binary=:all:

echo "Installing Python dependencies..."
pip install --only-binary=:all: -r setup_requirements.txt

echo "Reinstalling dependencies to ensure compatibility..."
pip uninstall -y numpy pyarrow snowflake-connector-python || true
pip install --only-binary=:all: -r setup_requirements.txt

echo "Installing SnowSQL CLI..."


# Add SnowSQL to PATH
export PATH="$HOME/.snowsql/bin:$PATH"

# (Optional) Persist to shell config for future use
if ! grep -q 'snowsql/bin' "$HOME/.bashrc"; then
  echo 'export PATH="$HOME/.snowsql/bin:$PATH"' >> "$HOME/.bashrc"
fi

# Confirm installation
if command -v snowsql &> /dev/null; then
  echo "SnowSQL installed successfully!"
else
  echo "SnowSQL installation failed."
  exit 1
fi



echo "Cleaning up any old containers..."
export COMPOSE_HTTP_TIMEOUT=300

docker-compose -f kafka/docker-compose.yml down -v --remove-orphans || true

export COMPOSE_HTTP_TIMEOUT=300
echo "Starting Zookeeper and Kafka using Docker..."
docker-compose -f kafka/docker-compose.yml up --build -d

# Wait until Kafka is ready
echo "Waiting for Kafka to be ready..."
MAX_RETRIES=60
RETRY_INTERVAL=10
RETRIES=0

while ! nc -z localhost 29092; do
  sleep $RETRY_INTERVAL
  RETRIES=$((RETRIES + 1))
  echo "Waiting for Kafka... ($RETRIES/$MAX_RETRIES)"
  if [ "$RETRIES" -ge "$MAX_RETRIES" ]; then
    echo "❌ Kafka did not start in expected time. Exiting..."
    exit 1
  fi
done

echo "Kafka is up and running!"

# Additional wait to ensure Kafka is fully ready
echo "Additional wait to ensure Kafka is fully ready..."
sleep 30

echo "Starting Kafka consumer in background..."
python3 kafka_consumer_to_snowflake.py &
CONSUMER_PID=$!
sleep 100

echo "Running mock data generator..."
python3 generator/mock_generator.py &
GENERATOR_PID=$!

# Let them run for 3 minutes
sleep 180

# Kill the mock data generator if still running
if ps -p $GENERATOR_PID > /dev/null; then
  kill $GENERATOR_PID
  echo "Mock data generator stopped."
fi

# Kill the Kafka consumer if still running
if ps -p $CONSUMER_PID > /dev/null; then
  kill $CONSUMER_PID
  echo "Kafka consumer stopped."
fi

echo "Creating Snowflake database, schema, and table..."

echo "Using Snowflake credentials:"
echo "Account: $SNOWFLAKE_ACCOUNT"
echo "User: $SNOWFLAKE_USER"
echo "Password: $SNOWFLAKE_PASSWORD"

snowsql -c snowflake_conn -f init_snowflake.sql

echo "Starting Airflow using Docker..."
# export COMPOSE_HTTP_TIMEOUT=300
# docker-compose -f kafka/docker-compose.yml up --build -d

# Wait a bit for Airflow webserver to be ready
echo "Waiting for Airflow webserver to be ready..."
sleep 100

# Unpause the DAG before triggering it
docker exec -i kafka-airflow-webserver-1 airflow dags unpause  transform_snowflake_data
docker exec -i kafka-airflow-webserver-1 airflow dags unpause  snowflake_to_bigquery

sleep 100

echo "Triggering Airflow DAG: transform_snowflake_data"
docker exec -i kafka-airflow-webserver-1 airflow dags trigger transform_snowflake_data
sleep 200

echo "Triggering Airflow DAG: snowflake_to_bigquery"
docker exec -i kafka-airflow-webserver-1 airflow dags trigger snowflake_to_bigquery


echo "Pipeline execution completed!"
