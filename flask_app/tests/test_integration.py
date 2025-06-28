import pytest
import paho.mqtt.publish as publish
import requests
import time
import json
import os

# --- Fixtures and Configuration -----------------------------------------

# Service hostnames are determined by docker-compose service names
MQTT_BROKER_HOST = os.environ.get("MQTT_BROKER_HOST", "mosquitto")
API_HOST = os.environ.get("API_HOST", "flask_app")
API_PORT = os.environ.get("API_PORT", 5001)
API_URL = f"http://{API_HOST}:{API_PORT}"

# Use a unique topic for testing to avoid interfering with the running app
TEST_TOPIC = "power/test"

@pytest.fixture(scope="module")
def wait_for_services():
    """Gives services time to start up."""
    # A more robust solution would be to poll the services
    time.sleep(10)

# --- Test Cases -----------------------------------------------------------

@pytest.mark.integration
def test_end_to_end_flow(wait_for_services):
    """
    Tests the full flow:
    1. Publish an MQTT message.
    2. Wait for the Flask app to process it.
    3. Call the API to verify the data was stored correctly.
    """
    # 1. Define and publish the test message
    device_id = 999
    test_payload = {
        "deviceCode": device_id,
        "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        "temp": 99.9,
        "humidity": 45.5,
        "brightness": 1000,
        "electric": 1.23
    }
    
    try:
        publish.single(
            TEST_TOPIC,
            payload=json.dumps(test_payload),
            hostname=MQTT_BROKER_HOST
        )
    except Exception as e:
        pytest.fail(f"Failed to publish to MQTT: {e}")

    # 2. Wait for message to be processed
    time.sleep(3) 

    # 3. Call the API to fetch data
    try:
        response = requests.get(f"{API_URL}/api/power_data?limit=5")
        response.raise_for_status() # Raises an exception for 4xx/5xx errors
        data = response.json()
    except Exception as e:
        pytest.fail(f"API request failed: {e}")

    # 4. Verify the data
    assert isinstance(data, list)
    assert len(data) > 0, "API returned no data"

    # Find our specific test record
    test_record = None
    for record in data:
        if record.get("device_code") == device_id:
            test_record = record
            break
            
    assert test_record is not None, f"Did not find test record for device {device_id} in API response"
    
    assert test_record["temperature"] == test_payload["temp"]
    assert test_record["humidity"] == test_payload["humidity"]
    assert test_record["brightness"] == test_payload["brightness"]
    assert test_record["electric"] == test_payload["electric"]
