from kafka import KafkaProducer
import json
import time
from faker import Faker

fake = Faker()

# Note: Humne MSK ka broker endpoint yahan dena hai. 
# Agar aapka script local chal raha hai aur broker internal hai, toh hum Kafka bootstrap servers ka address yahan add karenge.
# Filhal hum placeholder set kar rahe hain, aap apna MSK bootstrap servers yahan dalenge.
BOOTSTRAP_SERVERS = ['YOUR_MSK_BROKER_IP:9092'] # Isay hum abhi update karte hain

producer = KafkaProducer(
    bootstrap_servers=BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

print("Kafka Producer started... Sending data to topic 'hackathon-topic'")

while True:
    data = {
        "transaction_id": fake.uuid4(),
        "user_name": fake.name(),
        "amount": round(fake.random_number(digits=4) + fake.random.random(), 2),
        "timestamp": fake.iso8601()
    }
    
    producer.send('hackathon-topic', value=data)
    print(f"Sent: {data}")
    time.sleep(2)