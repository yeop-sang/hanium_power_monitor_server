import paho.mqtt.publish as publish
import json, time, random, datetime, os

MQTT_HOST = os.getenv("MQTT_BROKER_HOST", "localhost")   # 호스트에서 실행하므로 localhost
TOPIC     = "power/measurement"
DEVICE    = 1234

for i in range(10):
    payload = {
        "deviceCode": DEVICE,
        "timestamp": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "temp": round(random.uniform(22, 28), 1),
        "humidity": round(random.uniform(40, 60), 1),
        "brightness": random.randint(400, 900),
        "electric": round(random.uniform(800, 1500), 1)
    }
    publish.single(TOPIC, json.dumps(payload), hostname=MQTT_HOST)
    print("Published", payload)
    time.sleep(5)