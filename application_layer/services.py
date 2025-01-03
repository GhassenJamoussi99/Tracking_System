class Services:
    """
    @class Services
    @brief Contains configuration constants for MQTT broker and topics.
    """
    BROKER_ADDRESS = "172.16.2.160"
    MQTT_PORT = 1883
    
    # MQTT Topics
    # ts/{SUBSCRIBER}/{PUBLISHER}/{SERVICE}
    TOPIC_RFID_TAGS = "ts/alarm_controller/rfid_controller/show_tags"
    TOPIC_ALARM_STATUS = "ts/gui/alarm_controller/show_state"
    TOPIC_GUI_ALARM = "ts/alarm_controller/gui/deactivate_alarm"
    
    # MQTT Clients IDs
    MQTT_RFID_PUB = "rfid_publisher"
    MQTT_GUI_SUB_ALARM = "gui_subcriber"
    MQTT_GUI_PUB_ALARM = "gui_publisher"
    MQTT_ALARM_RFID_SUB = "alarm_rfid_subscriber"
    MQTT_ALARM_GUI_SUB = "alarm_gui_subscriber"