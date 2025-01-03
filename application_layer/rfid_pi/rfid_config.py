class RFIDConfig:
    """
    @brief Configuration class for the RFID reader.
    """

    reader_uri = "tmr:///dev/serial0"
    """
    @brief The URI of the RFID reader.
    @details This is the connection string used to communicate with the RFID reader.
    """

    region = "EU3"
    """
    @brief The region setting for the RFID reader.
    @details This specifies the regulatory region for the RFID reader.
    """

    reader_powers = [(1, 2700)]  # Antenna 1, Power 27 dBm
    """
    @brief The read powers for the RFID reader.
    @details This is a list of tuples where each tuple contains an antenna number and its corresponding power in dBm.
    """

    read_plan_protocol = "GEN2"
    """
    @brief The protocol to use for reading.
    @details Supported values are:
    - "GEN2": UPC GEN2
    - "ISO180006B": ISO 180006B
    - "UCODE": ISO 180006B UCODE
    - "IPX64": IPX (64kbps link rate)
    - "IPX256": IPX (256kbps link rate)
    - "ATA"
    @see https://github.com/gotthardp/python-mercuryapi
    """

    read_plan_antenna = [1]
    """
    @brief The list of antennas to use for reading.
    @details This specifies which antennas are used by the RFID reader.
    """

    timeout = 500
    """
    @brief The timeout for reading tags.
    @details This specifies the duration in milliseconds for which the RFID reader will attempt to read tags.
    """