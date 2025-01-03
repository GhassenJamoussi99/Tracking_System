import logging
from smartcard.CardRequest import CardRequest
from smartcard.Exceptions import CardRequestTimeoutException, NoCardException, CardConnectionException
from smartcard.CardType import AnyCardType
from smartcard import util
from application_layer.nfc_controller.nfc_config import NFCConfig

class NFCScanner():
    """ 
    @class NFCScanner
    @brief Low-level functions for interacting with NFC cards.
    """

    def __init__(self, timeout=0):
        """
        @brief Constructor for NFCScanner.
        @param timeout Timeout period for card scanning operations.
        """
        super().__init__()
        self.card_type = AnyCardType()
        self.request = CardRequest(timeout=timeout, cardType=self.card_type)

    def scan_card(self):
        """
        @brief Wait for an NFC card to be presented and return the service object if a card is detected.
        
        @return service The service object representing the detected card.
        @retval None If no card is detected within the timeout period.
        """
        try:
            service = self.request.waitforcard()
            logging.info("Card detected, attempting to connect...")
            return service
        except CardRequestTimeoutException:
            logging.info("No card detected, waiting...")
            return None

    def connect_card(self, scan_service):
        """
        @brief Establish a connection to the NFC card.
        
        @param scan_service The service object representing the detected card.
        @return conn The connection object if the connection is successful.
        @retval None If the card is not present or a connection cannot be established.
        """
        try:
            conn = scan_service.connection
            conn.connect()
            logging.info("Connection established.")
            return conn
        except NoCardException:
            logging.warning("No card present, continuing to wait.")
            return None
        except CardConnectionException as e:
            logging.error(f"Connection error: {e}")
            return None        
        except Exception as e:
            logging.exception("An unexpected error occurred")        
            return None

    def get_card_uid(self, conn):
        """
        @brief Send an APDU command to retrieve the UID (Unique Identifier) of the connected card.
        
        @param conn The connection object representing the active connection to the card.
        @return uid The UID of the card as a hexadecimal string.
        @return status The status word (SW1 SW2) from the APDU response.
        @retval None, None If the command transmission fails.
        """
        get_uid_cmd = util.toBytes(NFCConfig.APDU_COMMAND)
        try:
            data, sw1, sw2 = conn.transmit(get_uid_cmd)
            uid = util.toHexString(data)
            status = util.toHexString([sw1, sw2])
            return uid, status
        except CardConnectionException as e:
            logging.error(f"Failed to transmit APDU command: {e}")
            return None, None

    def get_card_atr(self, conn):
        """
        @brief Retrieve the ATR (Answer To Reset) of the connected card.
        
        @param conn The connection object representing the active connection to the card.
        @return atr The ATR of the card as a hexadecimal string.
        @retval None If retrieval fails.
        """
        try:
            atr = util.toHexString(conn.getATR())
            return atr
        except Exception as e:
            logging.error(f"Failed to get ATR: {e}")
            return None
