from time import sleep
import paho.mqtt.client as mqtt
import logging
import ast
import threading
import time 

from application_layer.device_db_service import DeviceDBService
from application_layer.services import Services
from application_layer.alarm_pi.alarm import Alarm

class AlarmService:
    """
    @brief A class to handle the alarm service using MQTT.
    """

    def __init__(self):
        """
        @brief Initializes the AlarmService class.
        """
        self.device_db_service = DeviceDBService()
        self.alarm = Alarm()
        self.broker_address = Services.BROKER_ADDRESS
        self.mqtt_port = Services.MQTT_PORT
        self.topic_rfid_tags = Services.TOPIC_RFID_TAGS
        self.topic_alarm_status = Services.TOPIC_ALARM_STATUS
        self.topic_gui_alarm = Services.TOPIC_GUI_ALARM

    def on_alarm_gui_sub_connect(self, client, userdata, flags, rc):
        """
        @brief Callback function for when the client receives a CONNACK response from the server.
        @param client The client instance for this callback.
        @param userdata The private user data as set in Client() or userdata_set().
        @param flags Response flags sent by the broker.
        @param rc The connection result.
        """
        if rc == 0:
            logging.info("AlarmService::Connected successfully to broker")
            client.subscribe(self.topic_gui_alarm)
            logging.info(f"AlarmService::Subscribed to topic {self.topic_gui_alarm}")
        else:
            logging.error(f"AlarmService::Connection failed with code {rc}")
    
    def on_alarm_gui_sub_message(self, client, userdata, msg):
        """
        @brief Callback function for when a PUBLISH message is received from the server.
        @param client The client instance for this callback.
        @param userdata The private user data as set in Client() or userdata_set().
        @param msg An instance of MQTTMessage, which contains topic, payload, qos, retain.
        """
        try:
            # Decode the received payload
            payload_str = msg.payload.decode()
            logging.info(f"AlarmService::Received message: '{payload_str}' on topic '{msg.topic}'")

            # Safely evaluate the string as a Python dictionary
            payload = ast.literal_eval(payload_str)

            # Extract the status of the alarm
            alarm_status = payload['alarm_status']
            logging.info(f"AlarmService::Alarm status: {alarm_status}")

            # Deactivate the alarm if the status is 'DEACTIVATE'
            if alarm_status == "DEACTIVATE":
                logging.info("AlarmService::Deactivating the alarm...")
                self.alarm.stop_alarm()
            else:
                logging.info("AlarmService::Alarm is still active")
        except Exception as e:
            logging.error(f"AlarmService::Error handling message: {e}")


    def on_alarm_rfid_connect(self, client, userdata, flags, rc):
        """
        @brief Callback function for when the client receives a CONNACK response from the server.
        @param client The client instance for this callback.
        @param userdata The private user data as set in Client() or userdata_set().
        @param flags Response flags sent by the broker.
        @param rc The connection result.
        """
        if rc == 0:
            logging.info("AlarmService::Connected successfully to broker")
            client.subscribe(self.topic_rfid_tags)
            logging.info(f"AlarmService::Subscribed to topic {self.topic_rfid_tags}")
        else:
            logging.error(f"AlarmService::Connection failed with code {rc}")

    def on_alarm_rfid_message(self, client, userdata, msg):
        """
        @brief Callback function for when a PUBLISH message is received from the server.
        @param client The client instance for this callback.
        @param userdata The private user data as set in Client() or userdata_set().
        @param msg An instance of MQTTMessage, which contains topic, payload, qos, retain.
        """
        try:
            # Decode the received payload
            payload_str = msg.payload.decode()
            logging.info(f"AlarmService::Received message: '{payload_str}' on topic '{msg.topic}'")

            # Safely evaluate the string as a Python dictionary
            payload = ast.literal_eval(payload_str)

            # Extract and decode the tag number (EPC)
            tag_nr = payload['tag']['epc'].decode('utf-8')
            logging.info(f"AlarmService::Tag number {tag_nr}")

            # Get the is_borrowed status of the device
            is_borrowed = self.device_db_service.get_is_borrowed_status_by_tag_number(tag_nr)

            # Activate alarm if false
            if is_borrowed == False:
                logging.info("AlarmService::Device is not borrowed, triggering the alarm...")
                self.alarm.start_alarm()
                
                # Create a payload for the alarm status message
                alarm_payload = {
                    "status": "ALARM",
                    "message": f"Device with tag number {tag_nr} is not borrowed"
                }
                alarm_payload_str = str(alarm_payload)
                # Publish the alarm status message
                self.mqtt_alarm_gui_client.publish(self.topic_alarm_status, alarm_payload_str)
                logging.info(f"AlarmService::Published alarm status: {alarm_payload_str} to topic '{self.topic_alarm_status}'")
            else:
                logging.info("AlarmService::Device is borrowed, the student can leave the room")
        except Exception as e:
            logging.error(f"AlarmService::Error handling message: {e}")

    def setup_mqtt_alarm_rfid_client(self):
        """
        @brief Sets up the MQTT client for publishing to topics.
        """
        self.mqtt_alarm_rfid_client = mqtt.Client(
            client_id=Services.MQTT_ALARM_RFID_SUB,
            userdata=None,
            protocol=mqtt.MQTTv311,
            transport="tcp"
        )
        self.mqtt_alarm_rfid_client.on_connect = self.on_alarm_rfid_connect
        self.mqtt_alarm_rfid_client.on_message = self.on_alarm_rfid_message
        self.mqtt_alarm_rfid_client.connect(self.broker_address, self.mqtt_port)

    def setup_mqtt_alarm_gui_client(self):
        """
        @brief Sets up the MQTT client for publishing messages.
        """
        self.mqtt_alarm_gui_client = mqtt.Client(
            client_id=Services.MQTT_ALARM_GUI_SUB,
            userdata=None,
            protocol=mqtt.MQTTv311,
            transport="tcp"
        )

        self.mqtt_alarm_gui_client.on_connect = self.on_alarm_gui_sub_connect
        self.mqtt_alarm_gui_client.on_message = self.on_alarm_gui_sub_message
        self.mqtt_alarm_gui_client.connect(self.broker_address, self.mqtt_port)

    def start(self):
        """
        @brief Starts the alarm service by setting up the MQTT client and starting the loop.
        """
        self.setup_mqtt_alarm_rfid_client()
        self.setup_mqtt_alarm_gui_client()

        threading.Thread(target=self.mqtt_alarm_rfid_client.loop_start, daemon=True).start()
        threading.Thread(target=self.mqtt_alarm_gui_client.loop_start, daemon=True).start()

        logging.info("AlarmService::AlarmService started and running")

        try:
            while True:
                time.sleep(1)  # Sleep for a short duration to prevent high CPU usage
        except KeyboardInterrupt:
            logging.info("AlarmService::AlarmService stopping due to keyboard interrupt")
            self.mqtt_alarm_rfid_client.loop_stop()
            self.mqtt_alarm_gui_client.loop_stop()
            logging.info("AlarmService::AlarmService stopped")