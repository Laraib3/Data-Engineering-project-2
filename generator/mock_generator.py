import json
import time
import random
import uuid
from datetime import datetime
from faker import Faker
from kafka import KafkaProducer
from dotenv import load_dotenv
import os

load_dotenv()

KAFKA_BROKER = os.getenv("KAFKA_BROKER")
TOPIC_NAME = os.getenv("TOPIC_NAME")

fake = Faker()

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

PRODUCTS = [
    {"item_id": "p_101", "product_name": "Bluetooth Speaker", "category": "Electronics", "price": 29.99},
    {"item_id": "p_102", "product_name": "HDMI Cable", "category": "Accessories", "price": 9.99},
    {"item_id": "p_103", "product_name": "Gaming Mouse", "category": "Electronics", "price": 49.99},
    {"item_id": "p_104", "product_name": "Coffee Mug", "category": "Home", "price": 14.99}
]

def generate_event():
    user_id = f"u_{fake.random_int(1000, 9999)}"
    items = random.choices(PRODUCTS, k=random.randint(1, 3))
    for item in items:
        item["quantity"] = random.randint(1, 3)

    total_amount = round(sum(item["price"] * item["quantity"] for item in items), 2)

    return {
        "event_id": str(uuid.uuid4()),
        "event_timestamp": datetime.utcnow().isoformat() + "Z",
        "user": {
            "user_id": user_id,
            "name": fake.name(),
            "email": fake.email(),
            "age": random.randint(18, 60),
            "gender": random.choice(["male", "female"]),
            "location": {
                "city": fake.city(),
                "state": fake.state(),
                "country": fake.country()
            }
        },
        "session": {
            "session_id": str(uuid.uuid4()),
            "device": random.choice(["mobile", "desktop", "tablet"]),
            "os": random.choice(["iOS", "Android", "Windows", "macOS"])
        },
        "order": {
            "order_id": f"o_{fake.random_int(10000, 99999)}",
            "items": items,
            "payment_method": random.choice(["credit_card", "paypal", "upi"]),
            "total_amount": total_amount,
            "currency": "USD",
            "status": random.choice(["paid", "pending", "failed"])
        }
    }

if __name__ == "__main__":
    print("Producing mock data to Kafka...")
    while True:
        event = generate_event()
        producer.send(TOPIC_NAME, value=event)
        print(f"Produced: {event}")
        time.sleep(1)
