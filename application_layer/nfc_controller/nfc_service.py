import logging
import time
import threading

from PyQt6.QtCore import QThread, pyqtSignal
from smartcard.Exceptions import NoCardException, CardConnectionException

from application_layer.nfc_controller.nfc_scanner import NFCScanner

class NFCService(QThread):
    """
    @class NFCService
    @brief High-level functions for managing NFC scanning.
    """
    
    # Signal emitted when a smart card is successfully scanned
    smart_card_scanned = pyqtSignal(str)

    def __init__(self, timeout=0):
        """
        @brief Constructor for NFCService.

        @param timeout The timeout period for scanning operations.
        """
        super().__init__()
        self._stop_event = threading.Event()
        self.nfc_scanner = NFCScanner(timeout=timeout)
        self.setObjectName("NFCServiceThread")

    def run(self):
        """
        @brief Continuously scan for NFC cards and process them when detected.
        
        This method is executed in a separate thread and runs a loop that 
        waits for NFC cards to be detected. When a card is detected, it 
        attempts to connect to the card, retrieve the ATR and UID, and then 
        emits a signal with the UID.
        """
        threading.current_thread().name = self.objectName()

        while not self._stop_event.is_set():
            # Scan for a card
            scan_service = self.nfc_scanner.scan_card()
            if scan_service is None:
                continue
            
            try:
                # Attempt to connect to the card
                conn = self.nfc_scanner.connect_card(scan_service)
                if conn is None:
                    continue
                
                # Get and log the ATR (Answer to Reset) of the card
                atr = self.nfc_scanner.get_card_atr(conn)
                logging.info(f"ATR = {atr}")

                # Get and log the UID (Unique Identifier) of the card
                uid, status = self.nfc_scanner.get_card_uid(conn)
                if uid:
                    logging.info(f"UID = {uid}, status = {status}")
                    # Emit the scanned card UID through the signal
                    self.smart_card_scanned.emit(str(uid))

                time.sleep(1)  # Pause to avoid rapid looping

            except NoCardException:
                logging.warning("No card present, continuing to wait.")
            except CardConnectionException as e:
                logging.error(f"Connection error: {e}")
            except Exception as e:
                logging.exception("An unexpected error occurred")

    def stop(self):
        """
        @brief Stop the NFC scanning process.
        
        Sets the stop event, which will cause the scanning loop in the run 
        method to terminate.
        """
        self._stop_event.set()    

    def reset(self):
        """
        @brief Reset the stop event to allow the scanning process to resume.
        
        Clears the stop event so that the scanning process can continue when 
        the run method is called again.
        """
        self._stop_event.clear()
