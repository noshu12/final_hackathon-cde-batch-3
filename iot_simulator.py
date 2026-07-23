import json
import time
import random
from datetime import datetime, timezone
import boto3

# AWS IoT Core client setup (ye automatically aapke local AWS CLI credentials use karega)
# Apne region ke mutabiq region change kar sakte hain (jaise us-east-1)
iot_client = boto3.client('iot-data', region_name='us-east-1')

# Apna IoT Core MQTT Topic yahan likhein (jo project ke mutabiq hai)
IOT_TOPIC = "iot-events"

def generate_iot_payload():
    devices = ["device_01", "device_02", "device_03", "device_04", "device_05"]
    device_id = random.choice(devices)
    
    # London coordinates as per project specs
    latitude = 51.5074 + random.uniform(-0.01, 0.01)
    longitude = -0.1278 + random.uniform(-0.01, 0.01)
    
    payload = {
        "device_id": device_id,
        "latitude": latitude,
        "longitude": longitude,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    return payload

if __name__ == "__main__":
    print("Starting IoT Sensor Simulation and publishing to AWS IoT Core... Press Ctrl+C to stop.")
    try:
        while True:
            data = generate_iot_payload()
            message_payload = json.dumps(data)
            
            # AWS IoT Core par data publish karna
            response = iot_client.publish(
                topic=IOT_TOPIC,
                qos=1,
                payload=message_payload
            )
            
            print(f"Published to IoT Core -> {message_payload}")
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("\nSimulation stopped by user.")