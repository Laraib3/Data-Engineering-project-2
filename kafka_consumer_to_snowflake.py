import json
import time
import os
from kafka import KafkaConsumer
import snowflake.connector

# Kafka Config
KAFKA_TOPIC = os.getenv('TOPIC_NAME', 'ecommerce_topic')
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BROKER', 'localhost:29092')

# Snowflake Config
SNOWFLAKE_CONFIG = {
    'user': os.getenv('SNOWFLAKE_USER'),
    'password': os.getenv('SNOWFLAKE_PASSWORD'),
    'account': os.getenv('SNOWFLAKE_ACCOUNT'),
    'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE'),
    'database': os.getenv('SNOWFLAKE_DATABASE'),
    'schema': os.getenv('SNOWFLAKE_SCHEMA')
}

# Connect to Kafka
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

# Connect to Snowflake
conn = snowflake.connector.connect(**SNOWFLAKE_CONFIG)
cursor = conn.cursor()

print("⏳ Consuming messages from Kafka and inserting into Snowflake...")

# Start timer
start_time = time.time()
timeout_seconds = 180  # 3 minutes

try:
    for message in consumer:
        # Exit loop after timeout
        if time.time() - start_time > timeout_seconds:
            print("⏰ Time limit reached. Stopping Kafka consumer...")
            break

        record = message.value
        print("📝 Received record:", record)

        # Insert into Snowflake using user_id as the ID
        cursor.execute(
            """
            INSERT INTO raw.kafka_events(id, raw_data)
            SELECT PARSE_JSON(%s):user_id, PARSE_JSON(%s)
            """,
            (json.dumps(record), json.dumps(record))
        )
        conn.commit()
        print(f"✅ Inserted record with ID: {record.get('user_id')}")

except KeyboardInterrupt:
    print("⛔ Stopped by user.")
finally:
    cursor.close()
    conn.close()
    consumer.close()
    print("✅ Kafka consumer and Snowflake connection closed.")
