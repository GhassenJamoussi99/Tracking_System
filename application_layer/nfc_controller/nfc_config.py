class NFCConfig:
    """
    @class NFCConfig
    @brief Configuration class for NFC settings.

    This class holds the configuration settings used for NFC operations.
    """
    
    APDU_COMMAND = "FF CA 00 00 00"
    """
    @brief Command to retrieve the card's UID.
    @details This APDU command is used to get the UID of an NFC card.
    """