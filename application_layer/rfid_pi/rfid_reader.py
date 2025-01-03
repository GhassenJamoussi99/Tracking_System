import mercury
import logging

class RFIDReader:
    """
    @brief A class to handle RFID reading using the Mercury API.
    """

    def __init__(self, reader_uri, region, read_powers, antenna_list, protocol, timeout):
        """
        @brief Initializes the RFIDReader class.
        @param reader_uri The URI of the RFID reader.
        @param region The region setting for the RFID reader.
        @param read_powers The read powers for the RFID reader.
        @param antenna_list The list of antennas to use.
        @param protocol The protocol to use for reading.
        @param timeout The timeout for reading tags.
        """
        self.reader = mercury.Reader(reader_uri)
        self.region = region
        self.read_powers = read_powers
        self.antenna_list = antenna_list
        self.protocol = protocol
        self.timeout = timeout
        self.setup_reader()

    def setup_reader(self):
        """
        @brief Sets up the RFID reader with the specified configurations.
        """
        self.reader.set_region(self.region)
        self.reader.set_read_powers(self.read_powers)
        self.reader.set_read_plan(self.antenna_list, self.protocol)

    def read_tags(self):
        """
        @brief Reads RFID tags using the configured reader.
        @return A list of tags read by the RFID reader.
        """
        try:
            tags = self.reader.read(self.timeout)
            return tags
        except Exception as e:
            logging.error(f"RFIDReader::Error reading tags: {e}")
            return []