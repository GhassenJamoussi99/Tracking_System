from PyQt6.QtCore import QObject, pyqtSignal
import logging 

class QRCodeScanner(QObject):
    """
    @class QRCodeScanner
    @brief A class to handle QR code scanning and signal emission.
    """
    device_qr_code_scanned = pyqtSignal(str)

    def __init__(self, parent=None):
        """
        @brief Constructor for QRCodeScanner.
        @param parent The parent QObject, if any.
        """
        super().__init__(parent)
        self.qr_code = ""

    def scan_qr_code(self, key):
        """
        @brief Processes the input key for QR code scanning.
        @param key The input key from the QR code scanner.
        """
        logging.info("QRCodeScanner::Processing QR Code Scanner")
        if key == '\r' or key == '\n':  # Enter key, assuming it's the end of the QR code
            if self.qr_code:  # Emit signal only if there's something to process
                self.device_qr_code_scanned.emit(self.qr_code)
                self.qr_code = ""
        else:
            self.qr_code += key