from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os
import json
import logging
from flask_socketio import SocketIO

from modules.mqtt_client import MQTTClient
from modules.database import Database
from modules.api import setup_routes

# Load environment variables from .env file
load_dotenv()

# --- Logging Setup -----------------------------------------------------
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

# Flask & SocketIO initialization
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# --- Initializations ---------------------------------------------------
try:
    db = Database()
    logging.info("Database pool initialized successfully.")
except Exception as e:
    logging.critical(f"Failed to initialize database: {e}", exc_info=True)
    db = None

# --- MQTT Message Handling ---------------------------------------------
def on_message_callback(payload):
    """
    Callback function to process incoming MQTT messages.
    Parses the JSON payload and inserts it into the database.
    """
    if not db:
        logging.warning("Database not available. Skipping message processing.")
        return

    try:
        data = json.loads(payload)
        
        # Extract data from payload
        device_code = data.get('deviceCode')
        timestamp = data.get('timestamp')
        temp = data.get('temp')
        humidity = data.get('humidity')
        brightness = data.get('brightness')
        electric = data.get('electric')

        # Basic validation
        if device_code is None or timestamp is None:
            logging.warning(f"Skipping message due to missing deviceCode or timestamp: {data}")
            return

        # Insert into database
        db.insert_reading(device_code, timestamp, temp, humidity, brightness, electric)
        logging.info(f"Successfully inserted reading for device {device_code}")

        # Emit data to connected WebSocket clients
        try:
            socketio.emit('reading', {
                'device_code': device_code,
                'timestamp': timestamp,
                'temperature': temp,
                'humidity': humidity,
                'brightness': brightness,
                'electric': electric
            })
        except Exception as e:
            logging.error(f"SocketIO emit failed: {e}")

    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON from payload: {payload}", exc_info=True)
    except Exception as e:
        logging.error(f"Error processing message: {e}", exc_info=True)

# Initialize MQTT client if the database is available
if db:
    try:
        main_topic = os.environ.get('MQTT_TOPIC', 'power/measurement')
        test_topic = os.environ.get('MQTT_TEST_TOPIC', 'power/test')
        
        mqtt_client = MQTTClient(
            on_message_callback=on_message_callback,
            topics=[main_topic, test_topic]
        )
        logging.info("MQTT Client initialized for topics: " + str([main_topic, test_topic]))
    except Exception as e:
        logging.error(f"Failed to initialize MQTT client: {e}", exc_info=True)
        mqtt_client = None
else:
    mqtt_client = None
    logging.warning("MQTT client not initialized because database is unavailable.")


# --- API Routes --------------------------------------------------------
if db:
    api_blueprint = setup_routes(db)
    app.register_blueprint(api_blueprint)
    logging.info("API routes registered.")
else:
    logging.warning("API routes not registered because database is unavailable.")


# --- Main Execution ----------------------------------------------------
if __name__ == '__main__':
    if mqtt_client:
        # Start MQTT client in a background thread
        mqtt_client.start()
        logging.info("MQTT client started in background.")
    
    # Start Flask app
    port = int(os.environ.get('FLASK_PORT', 5000))
    # Use SocketIO run to support WebSocket
    socketio.run(app, host='0.0.0.0', port=port)
