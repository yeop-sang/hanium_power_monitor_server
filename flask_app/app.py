from flask import Flask, request
from flask_cors import CORS
from dotenv import load_dotenv
import os
import json
import logging
from flask_socketio import SocketIO
import datetime
from flask_socketio import join_room, leave_room

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
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)

# Connected clients tracking
connected_clients = set()

# --- Socket.IO Event Handlers ---------------------------------------------
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    client_id = request.sid
    connected_clients.add(client_id)
    logging.info(f"Client {client_id} connected. Total clients: {len(connected_clients)}")
    
    # Send connection confirmation with server status
    socketio.emit('connection_status', {
        'status': 'connected',
        'client_id': client_id,
        'server_time': datetime.datetime.now().isoformat(),
        'mqtt_connected': mqtt_client.client.is_connected() if mqtt_client else False,
        'db_available': db is not None
    }, room=client_id)

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    client_id = request.sid
    connected_clients.discard(client_id)
    logging.info(f"Client {client_id} disconnected. Total clients: {len(connected_clients)}")

@socketio.on('ping')
def handle_ping():
    """Handle ping from client for connection health check"""
    client_id = request.sid
    logging.debug(f"Ping received from client {client_id}")
    socketio.emit('pong', {
        'timestamp': datetime.datetime.now().isoformat(),
        'client_id': client_id
    }, room=client_id)

@socketio.on('get_latest_data')
def handle_get_latest_data():
    """Handle client request for latest data"""
    client_id = request.sid
    
    if not db:
        socketio.emit('error', {
            'type': 'database_error',
            'message': 'Database not available'
        }, room=client_id)
        return
    
    try:
        # Get latest reading from database
        latest_data = db.fetch_power_data(limit=1)
        if latest_data:
            data = latest_data[0]
            socketio.emit('latest_data', {
                'device_code': data.get('device_code'),
                'timestamp': data.get('timestamp').isoformat() if data.get('timestamp') else None,
                'temperature': float(data.get('temperature')) if data.get('temperature') else None,
                'humidity': float(data.get('humidity')) if data.get('humidity') else None,
                'brightness': data.get('brightness'),
                'electric': float(data.get('electric')) if data.get('electric') else None
            }, room=client_id)
        else:
            socketio.emit('error', {
                'type': 'no_data',
                'message': 'No data available'
            }, room=client_id)
            
    except Exception as e:
        logging.error(f"Error fetching latest data for client {client_id}: {e}")
        socketio.emit('error', {
            'type': 'fetch_error',
            'message': 'Failed to fetch latest data'
        }, room=client_id)

@socketio.on('join_room')
def handle_join_room(data):
    """Handle client joining a specific room"""
    client_id = request.sid
    room = data.get('room', 'general')
    join_room(room)
    logging.info(f"Client {client_id} joined room: {room}")
    socketio.emit('room_joined', {'room': room}, room=client_id)

@socketio.on('leave_room')
def handle_leave_room(data):
    """Handle client leaving a specific room"""
    client_id = request.sid
    room = data.get('room', 'general')
    leave_room(room)
    logging.info(f"Client {client_id} left room: {room}")
    socketio.emit('room_left', {'room': room}, room=client_id)

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
