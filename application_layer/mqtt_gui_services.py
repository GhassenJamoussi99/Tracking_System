import threading
import logging
import paho.mqtt.client as mqtt
from PyQt6.QtCore import QObject, pyqtSignal

from application_layer.services import Services

class MQTTGuiServices(QObject):
    send_alert = pyqtSignal()

    def __init__(self, parent=None):
        """
        @brief Constructor for MQTTGuiServices.
        @param parent The parent QObject, if any.
        """
        super().__init__(parent)
        self.broker_address = Services.BROKER_ADDRESS
        self.mqtt_port = Services.MQTT_PORT

    def on_subscriber_connect(self, client, userdata, flags, rc):
        """
        @brief Callback for when the subscriber client connects to the broker.
        @param client The client instance for this callback.
        @param userdata The private user data as set in Client() or userdata_set().
        @param flags Response flags sent by the broker.
        @param rc The connection result.
        """
        if rc == 0:
            self.mqtt_subscriber_client.subscribe(Services.TOPIC_ALARM_STATUS)
            logging.info("MQTTGuiServices:: ts/gui/alarm_controller/show_state")
            logging.info("MQTTGuiServices:: Connected successfully to broker")
        else:
            logging.error(f"MQTTGuiServices::Connection failed with code {rc}")

    def on_publisher_connect(self, client, userdata, flags, rc):
        """
        @brief Callback for when the publisher client connects to the broker.
        @param client The client instance for this callback.
        @param userdata The private user data as set in Client() or userdata_set().
        @param flags Response flags sent by the broker.
        @param rc The connection result.
        """
        if rc == 0:
            logging.info("MQTTGuiServices:: ts/alarm_controller/gui/deactivate_alarm")
            logging.info("MQTTGuiServices::Connected successfully to broker")
        else:
            logging.error(f"MQTTGuiServices::Connection failed with code {rc}")

    def check_alarm_state(self, client, userdata, msg):
        """
        @brief Callback for when a message is received from the broker.
        @param client The client instance for this callback.
        @param userdata The private user data as set in Client() or userdata_set().
        @param msg An instance of MQTTMessage, which contains topic, payload, qos, retain.
        """
        logging.info(f"MQTTGuiServices::Received message: '{msg.payload.decode()}' on topic '{msg.topic}'")
        self.send_alert.emit()
        
    def setup_mqtt_subscriber_client(self):
        """
        @brief Sets up the MQTT subscriber client.
        """
        self.mqtt_subscriber_client = mqtt.Client(
            client_id=Services.MQTT_GUI_SUB_ALARM,
            userdata=None,
            protocol=mqtt.MQTTv311,
            transport="tcp"
        )
        self.mqtt_subscriber_client.on_connect = self.on_subscriber_connect
        self.mqtt_subscriber_client.on_message = self.check_alarm_state
        self.mqtt_subscriber_client.connect(self.broker_address, self.mqtt_port)  

    def setup_mqtt_publisher_client(self):
        """
        @brief Sets up the MQTT publisher client.
        """
        self.mqtt_publisher_client = mqtt.Client(
            client_id=Services.MQTT_GUI_PUB_ALARM,
            userdata=None,
            protocol=mqtt.MQTTv311,
            transport="tcp"
        )
        self.mqtt_publisher_client.on_connect = self.on_publisher_connect
        self.mqtt_publisher_client.connect(self.broker_address, self.mqtt_port)

    def send_deactivation_command(self):
        """
        @brief Sends a deactivation command to the alarm.
        """
        payload = {
            "alarm_status": "DEACTIVATE"
        }
        self.mqtt_publisher_client.publish(Services.TOPIC_GUI_ALARM, str(payload))

    def setup_mqtt_gui_services(self):
        """
        @brief Sets up the MQTT GUI services, including publisher and subscriber clients.
        """
        self.setup_mqtt_publisher_client()
        self.setup_mqtt_subscriber_client()

        # Start the MQTT client loops in separate threads
        threading.Thread(target=self.mqtt_publisher_client.loop_start, daemon=True).start()
        threading.Thread(target=self.mqtt_subscriber_client.loop_start, daemon=True).start()