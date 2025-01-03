import mysql.connector
import logging
from data_layer.config import DATABASE_CONFIG

class DeviceDao:
    """
    @class DeviceDao
    @brief Data Access Object (DAO) class for interacting with the devices table in the database.
    
    This class provides methods to perform CRUD (Create, Read, Update, Delete) operations on the devices table.
    """

    def __init__(self):
        """
        @brief Constructor for DeviceDao.
        
        Initializes the database connection and cursor.
        """
        self.conn = mysql.connector.connect(**DATABASE_CONFIG)
        self.cursor = self.conn.cursor()

    def __del__(self):
        """
        @brief Destructor for DeviceDao.
        
        Closes the database cursor and connection when the instance is destroyed.
        """
        self.cursor.close()
        self.conn.close()

    def add_device(self, name, is_borrowed, date, borrower_id, qr_code):
        """
        @brief Adds a new device to the devices table.
        
        @param name The name of the device.
        @param is_borrowed A boolean indicating whether the device is borrowed.
        @param date The date associated with the device record.
        @param borrower_id The ID of the borrower.
        @param qr_code The QR code associated with the device.
        """
        self.cursor.execute(
            "INSERT INTO devices (name, is_borrowed, date, borrower_id, qr_code) VALUES (%s, %s, %s, %s, %s)",
            (name, is_borrowed, date, borrower_id, qr_code)
        )
        self.conn.commit()
        logging.info(f"DeviceDao::Added device: {name}")

    def get_all_devices(self):
        """
        @brief Retrieves all devices from the devices table.
        
        @return A list of tuples, each representing a device record.
        """
        self.cursor.execute("SELECT * FROM devices")
        devices = self.cursor.fetchall()
        logging.info("DeviceDao::Retrieved all devices")
        return devices
    
    def get_device_name_from_qr_code(self, qr_code):
        """
        @brief Retrieves the device name associated with the given QR code.
        
        @param qr_code The QR code of the device.
        @return The name of the device if found, otherwise None.
        """
        self.cursor.execute("SELECT name FROM devices WHERE qr_code = %s", (qr_code,))
        device = self.cursor.fetchone()
        if device:
            logging.info(f"DeviceDao::Retrieved device name from QR code: {qr_code}")
            return device[0]  # Return the device name
        else:
            logging.warning(f"DeviceDao::No device found with QR code: {qr_code}")
            return None
        
    def get_is_borrowed_status_by_tag_number(self, tag_number):
        """
        @brief Retrieves the borrowed status of a device based on its tag number.
        
        @param tag_number The tag number of the device.
        @return The borrowed status (True/False) if found, otherwise None.
        """
        self.cursor.execute(
            "SELECT is_borrowed FROM devices WHERE tag_nr = %s", 
            (tag_number,)
        )
        result = self.cursor.fetchone()
        if result is not None:
            logging.info(f"DeviceDao::Retrieved borrow status for tag number: {tag_number}")
            return result[0]  # Assuming is_borrowed is a boolean or integer (1 or 0)
        else:
            logging.warning(f"DeviceDao::No item found with tag number: {tag_number}")
            return None
        
    def get_is_borrowed_status_by_device_id(self, device_id):
        """
        @brief Retrieves the borrowed status of a device based on its ID.
        
        @param device_id The ID of the device.
        @return The borrowed status (True/False) if found, otherwise None.
        """
        self.cursor.execute("SELECT is_borrowed FROM devices WHERE id = %s", (device_id,))
        result = self.cursor.fetchone()
        if result is not None:
            logging.info(f"DeviceDao::Retrieved borrow status for device ID: {device_id}")
            return result[0]  # Assuming is_borrowed is a boolean or integer (1 or 0)
        else:
            logging.warning(f"DeviceDao::No item found with ID: {device_id}")
            return None
        
    def get_device_by_name(self, name):
        """
        @brief Retrieves a device by its name.
        
        @param name The name of the device.
        @return A tuple containing the device's ID and name if found.
        """
        self.cursor.execute("SELECT id, name FROM devices WHERE name = %s", (name,))
        device = self.cursor.fetchone()
        logging.info(f"DeviceDao::Retrieved device by name: {name}")
        return device

    def update_device(self, device_id, name=None, is_borrowed=None, borrower_id=None, qr_code=None, date=None):
        """
        @brief Updates a device's information in the database.
        
        @param device_id The ID of the device to be updated.
        @param name The new name of the device (optional).
        @param is_borrowed The new borrowed status of the device (optional).
        @param borrower_id The new borrower ID of the device (optional).
        @param qr_code The new QR code of the device (optional).
        @param date The new date associated with the device record (optional).
        """
        query = "UPDATE devices SET "
        params = []
        if name:
            query += "name = %s, "
            params.append(name)
        if is_borrowed is not None:
            query += "is_borrowed = %s, "
            params.append(is_borrowed)
            # Clear borrower ID if is_borrowed becomes False
            if is_borrowed == False:
                query += "borrower_id = %s, "
                params.append(None)
        if date:
            query += "date = %s, "
            params.append(date)
        if borrower_id:
            query += "borrower_id = %s, "
            params.append(borrower_id)
        if qr_code:
            query += "qr_code = %s, "
            params.append(qr_code)
        query = query.rstrip(', ')
        query += " WHERE id = %s"
        params.append(device_id)

        self.cursor.execute(query, tuple(params))
        self.conn.commit()
        logging.info(f"DeviceDao::Updated device ID: {device_id}")

    def delete_device(self, device_id):
        """
        @brief Deletes a device from the database.
        
        @param device_id The ID of the device to be deleted.
        """
        self.cursor.execute("DELETE FROM devices WHERE id = %s", (device_id,))
        self.conn.commit()
        logging.info(f"DeviceDao::Deleted device ID: {device_id}")

    def get_all_device_names(self):
        """
        @brief Retrieves all device names from the devices table.
        
        @return A list of device names.
        """
        self.cursor.execute("SELECT name FROM devices")
        device_names = [name[0] for name in self.cursor.fetchall()]
        logging.info("DeviceDao::Retrieved all device names")
        return device_names

    def refresh_connection(self):
        """
        @brief Refreshes the database connection.
        
        This method is used to refresh the database connection in case of a disconnect.
        """
        """
        @brief Refreshes the database connection.
        """
        self.cursor.close()
        self.conn.close()
        self.conn = mysql.connector.connect(**DATABASE_CONFIG)
        self.cursor = self.conn.cursor()
        logging.info("DeviceDao::Refreshed database connection")