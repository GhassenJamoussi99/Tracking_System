import logging
from data_access_layer.device_dao import DeviceDao
import datetime

class DeviceDBService:
    def __init__(self):
        """
        @brief Constructor for DeviceDBService.
        """
        self.device_dao = DeviceDao()
        self.logger = logging.getLogger(__name__)

    def add_device(self, name, qr_code, is_borrowed=False, borrower_id=None):
        """
        @brief Adds a new device to the database.
        @param name The name of the device.
        @param qr_code The QR code of the device.
        @param is_borrowed A boolean indicating whether the device is borrowed.
        @param borrower_id The ID of the borrower (optional).
        """
        date = datetime.datetime.now() if is_borrowed else None
        self.device_dao.add_device(name, is_borrowed, date, borrower_id, qr_code)
        self.logger.info(f"DeviceDBService: Added device {name}")

    def get_all_devices(self):
        """
        @brief Retrieves all devices from the database.
        @return A list of all devices.
        """
        devices = self.device_dao.get_all_devices()
        self.logger.info("DeviceDBService: Retrieved all devices")
        return devices

    def get_id_from_device_name(self, device_name):
        """
        @brief Retrieves the ID of a device based on its name.
        @param device_name The name of the device.
        @return The ID of the device, or None if not found.
        """
        device_id = self.device_dao.get_device_by_name(device_name)
        self.logger.info(f"DeviceDBService: Retrieved ID for device {device_name}")
        return device_id[0] if device_id else None

    def get_is_borrowed_status_by_tag_number(self, tag_number):
        """
        @brief Retrieves the borrowed status of a device based on its tag number.
        @param tag_number The tag number of the device.
        @return The borrowed status (True/False) of the device.
        """
        is_borrowed = self.device_dao.get_is_borrowed_status_by_tag_number(tag_number)
        self.logger.info(f"DeviceDBService: Retrieved borrow status for tag number {tag_number}: {is_borrowed}")
        return is_borrowed

    def get_is_borrowed_status_by_device_id(self, device_id):
        """
        @brief Retrieves the borrowed status of a device based on its ID.
        @param device_id The ID of the device.
        @return The borrowed status (True/False) of the device.
        """
        is_borrowed = self.device_dao.get_is_borrowed_status_by_device_id(device_id)
        self.logger.info(f"DeviceDBService: Retrieved borrow status for device ID {device_id}: {is_borrowed}")
        return is_borrowed
    
    def get_device_name_from_qr_code(self, qr_code):
        """
        @brief Retrieves the name of a device based on its QR code.
        @param qr_code The QR code of the device.
        @return The name of the device.
        """
        device_name = self.device_dao.get_device_name_from_qr_code(qr_code)
        self.logger.info(f"DeviceDBService: Retrieved device_name for qr_code {qr_code}")            
        return device_name
        
    def update_device(self, device_id, name=None, borrower_id=None, qr_code=None, is_borrowed=None):
        """
        @brief Updates the details of a device in the database.
        @param device_id The ID of the device to update.
        @param name The new name of the device (optional).
        @param borrower_id The new borrower ID of the device (optional).
        @param qr_code The new QR code of the device (optional).
        @param is_borrowed The new borrowed status of the device (optional).
        """
        date = datetime.datetime.now() if is_borrowed else None
        self.device_dao.update_device(device_id, name, is_borrowed, borrower_id, qr_code, date)
        self.logger.info(f"DeviceDBService: Updated device ID {device_id}")

    def borrow_device(self, device_id, name=None, borrower_id=None, qr_code=None, is_borrowed=True):
        """
        @brief Marks a device as borrowed in the database.
        @param device_id The ID of the device to update.
        @param name The new name of the device (optional).
        @param borrower_id The new borrower ID of the device (optional).
        @param qr_code The new QR code of the device (optional).
        @param is_borrowed The new borrowed status of the device (default is True).
        """
        date = datetime.datetime.now() if is_borrowed else None
        self.device_dao.update_device(device_id, name, is_borrowed, borrower_id, qr_code, date)
        self.logger.info(f"DeviceDBService: Updated device ID {device_id}")

    def return_device(self, device_id, name=None, borrower_id=None, qr_code=None, is_borrowed=False):
        """
        @brief Marks a device as returned in the database.
        @param device_id The ID of the device to update.
        @param name The new name of the device (optional).
        @param borrower_id The new borrower ID of the device (optional).
        @param qr_code The new QR code of the device (optional).
        @param is_borrowed The new borrowed status of the device (default is False).
        """
        date = datetime.datetime.now() if is_borrowed else None
        self.device_dao.update_device(device_id, name, is_borrowed, borrower_id, qr_code, date)
        self.logger.info(f"DeviceDBService: Updated device ID {device_id}")

    def delete_device(self, device_id):
        """
        @brief Deletes a device from the database.
        @param device_id The ID of the device to delete.
        """
        self.device_dao.delete_device(device_id)
        self.logger.info(f"DeviceDBService: Deleted device ID {device_id}")

    def get_all_device_names(self):
        """
        @brief Retrieves all device names from the database.
        @return A list of all device names.
        """
        device_names = self.device_dao.get_all_device_names()
        self.logger.info("DeviceDBService: Retrieved all device names")
        return device_names
    
    def refresh_connection(self):
        """
        @brief Refreshes the database connection.
        """
        self.device_dao.refresh_connection()
        self.logger.info("DeviceDBService: Refreshed connection")