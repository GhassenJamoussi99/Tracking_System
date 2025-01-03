from time import sleep
import paho.mqtt.client as mqtt
import logging

from application_layer.rfid_pi.rfid_config import RFIDConfig
from application_layer.rfid_pi.rfid_reader import RFIDReader
from application_layer.services import Services

class RFIDService:
    """
    @brief A class to handle RFID reading and MQTT publishing.
    """

    def __init__(self):
        """
        @brief Initializes the RFIDService class.
        """
        self.broker_address = Services.BROKER_ADDRESS
        self.mqtt_port = Services.MQTT_PORT
        self.topic_rfid_tags = Services.TOPIC_RFID_TAGS
        self.mqtt_client = None
        self.rfid_reader = RFIDReader(RFIDConfig.reader_uri,
                                      RFIDConfig.region,
                                      RFIDConfig.reader_powers,
                                      RFIDConfig.read_plan_antenna,
                                      RFIDConfig.read_plan_protocol,
                                      RFIDConfig.timeout)

    def on_connect(self, client, userdata, flags, rc):
        """
        @brief Callback function for when the client receives a CONNACK response from the server.
        @param client The client instance for this callback.
        @param userdata The private user data as set in Client() or userdata_set().
        @param flags Response flags sent by the broker.
        @param rc The connection result.
        """
        if rc == 0:
            logging.info("RFIDService::Connected successfully to broker")
        else:
            logging.error(f"RFIDService::Connection failed with code {rc}")

    def setup_mqtt_client(self):
        """
        @brief Sets up the MQTT client for connecting to the broker.
        """
        self.mqtt_client = mqtt.Client(
            client_id=Services.MQTT_RFID_PUB,
            userdata=None,
            protocol=mqtt.MQTTv311,
            transport="tcp"
        )
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.connect(self.broker_address, self.mqtt_port)

    def publish_tags(self, tags):
        """
        @brief Publishes RFID tags to the MQTT broker.
        @param tags A list of RFID tags to publish.
        """
        for tag in tags:
            payload = {
                "tag": {
                    "epc": tag.epc,
                    "rssi": tag.rssi
                }
            }
            self.mqtt_client.publish(self.topic_rfid_tags, str(payload))
            logging.info(f"RFIDService::Published: {payload} to {self.topic_rfid_tags}")

    def read_rfid_tags(self):
        """
        @brief Reads RFID tags and publishes them to the MQTT broker.
        """
        try:
            while True:
                tags = self.rfid_reader.read_tags()
                if not tags:
                    logging.warning("RFIDService::No tags found")
                else:
                    self.publish_tags(tags)
        except Exception as e:
            logging.error(f"RFIDService::Error: {e}")

    def start(self):
        """
        @brief Starts the RFID service by setting up the MQTT client and reading RFID tags.
        """
        self.setup_mqtt_client()
        self.mqtt_client.loop_start()  # Start the MQTT client loop
        self.read_rfid_tags()