import paho.mqtt.client as mqtt
import os
import threading
import time
import logging

class MQTTClient:
    def __init__(self, on_message_callback, topics=['power/measurement']):
        self.broker = os.environ.get('MQTT_BROKER', 'mosquitto')
        self.port = int(os.environ.get('MQTT_PORT', 1883))
        self.topics = topics
        self.client_id = f'flask-mqtt-client-{os.getpid()}'
        self.on_message_callback = on_message_callback
        
        self.client = mqtt.Client(client_id=self.client_id)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logging.info("Connected to MQTT Broker!")
            
            # Subscribe to all topics in the list
            for topic in self.topics:
                self.client.subscribe(topic)
                logging.info(f"Subscribed to topic: {topic}")
        else:
            logging.error(f"Failed to connect to MQTT broker, return code {rc}")

    def on_message(self, client, userdata, msg):
        try:
            # Pass the received message to the callback function provided during initialization
            self.on_message_callback(msg.payload.decode('utf-8'))
        except Exception as e:
            logging.error(f"Error in on_message_callback: {e}", exc_info=True)

    def start(self):
        """Connects to the broker and starts the network loop in a separate thread."""
        try:
            self.client.connect(self.broker, self.port, 60)
            
            # Start the network loop in a separate thread to avoid blocking
            thread = threading.Thread(target=self.client.loop_forever)
            thread.daemon = True
            thread.start()
            logging.info("MQTT client network loop started.")
        except ConnectionRefusedError:
            logging.error("Connection to MQTT broker refused. Check if the broker is running and accessible.")
        except Exception as e:
            logging.error(f"Could not start MQTT client: {e}", exc_info=True)
            # Optionally re-raise or handle the inability to connect
            raise

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()
        logging.info("MQTT client disconnected.")


