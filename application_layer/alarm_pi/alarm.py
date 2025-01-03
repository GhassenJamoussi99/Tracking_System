import RPi.GPIO as GPIO
import logging

from application_layer.alarm_pi.alarm_config import AlarmConfig

class Alarm:
    """
    @brief A class to control an alarm system using a relay.
    """

    def __init__(self):
        """
        @brief Initializes the Alarm class.
        @param relay_pin The GPIO pin connected to the relay. Default is 17.
        """
        self.relay_pin = AlarmConfig.RELAY_PIN
        self.setup_gpio()

    def setup_gpio(self):
        """
        @brief Sets up the GPIO mode and initializes the relay pin.
        """
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.relay_pin, GPIO.OUT)
        self.turn_off_relay()

    def turn_off_relay(self):
        """
        @brief Turns off the relay.
        """
        logging.info("Alarm::turn_off_relay")
        GPIO.output(self.relay_pin, GPIO.LOW)

    def turn_on_relay(self):
        """
        @brief Turns on the relay.
        """
        logging.info("Alarm::turn_on_relay")
        GPIO.output(self.relay_pin, GPIO.HIGH)

    def start_alarm(self):
        """
        @brief Starts the alarm by turning on the relay.
        """
        logging.info("Alarm::start_alarm")
        self.turn_on_relay()

    def stop_alarm(self):
        """
        @brief Stops the alarm by turning off the relay.
        """
        logging.info("Alarm::stop_alarm")
        self.turn_off_relay()