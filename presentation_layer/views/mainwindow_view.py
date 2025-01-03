import logging
import paho.mqtt.client as mqtt

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QLineEdit

from presentation_layer.views.mainwindow_view_ui import Ui_MainWindow
from presentation_layer.controllers.virtual_keybord import VirtualKeyboard, CustomLineEdit
from presentation_layer.controllers.password_checker import PasswordChecker

from application_layer.device_db_service import DeviceDBService
from application_layer.student_db_service import StudentDBService
from application_layer.states import UserAction
from application_layer.states import AdminAction
from application_layer.states import ScanMode
from application_layer.services import Services
from application_layer.mqtt_gui_services import MQTTGuiServices
from application_layer.qr_controller.qr_scanner import QRCodeScanner
from application_layer.nfc_controller.nfc_service import NFCService

from data_layer.config import ADMIN_PASSWORD

# NOTES:
# Page_1 : Start page
# Page_2 : Scanning student card using NFC Scanner
# Page_3 : Scanning device using QR Code Scanner
# Page_4 : Device assigned successfully
# Page_Actions : Borrow Return Admin
# Page_Admin : Admin functions (Deactivate Alarm/Home)
# Page_Password : For the admin 

class CMainwindowView(QMainWindow):
    """
    @brief Main window view class for the tracking system.

    This class handles the main window UI and controls the flow of the application,
    including user actions like borrowing, returning devices, and admin functions.
    """

    def __init__(self, parent=None):
        """
        @brief Constructor for CMainwindowView.

        Initializes the main window, sets up the UI, connects signals, and initializes services.

        @param parent The parent widget.
        """
        super().__init__(parent=parent)
        self.current_student_id = None  # type: int
        self.current_device_id = None  # type: int
        self.current_student_name = None  # type: str
        self.current_device_name = None  # type: str
        self.current_user_action = None  # type: UserAction
        self.current_admin_action = None  # type: AdminAction
        self.current_scan_mode = None  # type: ScanMode
        self.msg_box = None  # type: QMessageBox
        self.admin_password = ADMIN_PASSWORD  # type: str

        self.ui = Ui_MainWindow()
        self.device_db_service = DeviceDBService()
        self.student_db_service = StudentDBService()

        self.mqtt_gui_services = MQTTGuiServices()
        self.mqtt_gui_services.send_alert.connect(self.show_alarm_alert)

        self.matriculation_numbers = self.student_db_service.get_all_matriculation_numbers()
        self.device_names = self.device_db_service.get_all_device_names()
        
        self.nfc_service = NFCService()
        self.nfc_service.smart_card_scanned.connect(self.display_student_name)
        
        self.qr_code_scanner = QRCodeScanner()
        self.qr_code_scanner.device_qr_code_scanned.connect(self.display_device_name)
               
        self._init_ui()
        self._connect_signals()
        self.mqtt_gui_services.setup_mqtt_gui_services()
        self._setup_virtual_numeric_keyboard()

    def _init_ui(self):
        """
        @brief Initializes the user interface.

        Sets up the UI components and sets the initial page.
        """
        self.ui.setupUi(self)   
        self.setWindowTitle("Tracking System")
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_1)

    def show_keyboard(self):
        """
        @brief Shows the virtual keyboard.

        Displays the virtual keyboard widget.
        """
        self.keyboard.show()

    def _connect_signals(self):
        """
        @brief Connects UI signals to their respective slots.

        Sets up the signal-slot connections for UI interaction.
        """
        self.ui.start_button.clicked.connect(self.start_button_clicked)

        self.ui.confirm_button.clicked.connect(self.confirm_button_clicked)
        self.ui.confirm_button_1.clicked.connect(self.confirm_button_1_clicked)

        self.ui.back_button.clicked.connect(self.back_button_clicked)
        self.ui.back_button_1.clicked.connect(self.back_button_1_clicked)
        self.ui.back_button_2.clicked.connect(self.back_button_2_clicked)

        self.ui.home_button.clicked.connect(self.home_button_clicked)
        self.ui.borrow_button.clicked.connect(lambda: self.action_button_clicked(UserAction.BORROW))
        self.ui.return_button.clicked.connect(lambda: self.action_button_clicked(UserAction.RETURN))
        self.ui.admin_submit_button.clicked.connect(self.admin_submit_button_clicked)
        self.ui.admin_button.clicked.connect(self.admin_button_clicked)
        self.ui.home_button_2.clicked.connect(self.home_button_clicked)
        self.ui.deactivate_alarm.clicked.connect(self.deactivate_alarm_clicked)
        self.ui.home_button_3.clicked.connect(self.home_button_clicked)
        
        # Initialize PasswordChecker
        self.password_checker = PasswordChecker(self.admin_password)
        self.password_checker.password_verified.connect(self.on_password_verified)
        self.password_checker.password_failed.connect(self.on_password_failed)

    #################################  Home Page  ###############################
    def start_button_clicked(self):
        """
        @brief Slot for start button click event.

        Transitions the UI to the actions page.
        """
        logging.info("Start button clicked")
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_actions)

    #################################  PAGE - ACTION Page  ######################
    def action_button_clicked(self, action):
        """
        @brief Handles action button clicks for borrowing, returning, or admin actions.

        Resets device and student details, disables the confirm button, and starts the NFC scanner.

        @param action The user action selected (borrow, return, admin).
        """
        logging.info("Action button clicked")
        self.reset_device_student_details()
        self.disable_confirm_button()
        self.set_user_action(action)

        if (action == UserAction.RETURN):
            self.ui.stackedWidget.setCurrentWidget(self.ui.page_3)
            self.current_scan_mode = ScanMode.QR_CODE
        else:
            self.ui.stackedWidget.setCurrentWidget(self.ui.page_2)
            self.start_nfc_scanner()
            self.current_scan_mode = ScanMode.NFC

    ########################## PAGE 2 - Scan Student Card  ######################
    def confirm_button_clicked(self):
        """
        @brief Slot for confirm button click event on page 2.

        Stops the NFC scanner and transitions the UI to the device scanning page.
        """
        logging.info("Confirm button 1 clicked")
        self.stop_nfc_scanner()
        logging.debug("Student name = {} ".format(self.current_student_name))
        logging.debug("current_student_id = {} ".format(self.current_student_id))
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_3)
        logging.debug("Student name = {} ".format(self.current_student_name))
        self.current_scan_mode = ScanMode.QR_CODE

    def back_button_clicked(self):
        """
        @brief Slot for back button click event on page 2.

        Stops the NFC scanner and returns to the actions page.
        """
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_actions)
        self.stop_nfc_scanner()

    ####################### PAGE 3 - Scan Device QR Codes  ######################
    def confirm_button_1_clicked(self):
        """
        @brief Slot for confirm button click event on page 3.

        Processes the borrow or return action and displays the result.
        """
        try:
            logging.info("Confirm button 2 clicked")
            logging.debug("Device name = {} ".format(self.current_device_name))
            self.ui.stackedWidget.setCurrentWidget(self.ui.page_4)
            logging.debug("current id = {}".format(self.current_student_id))
            logging.debug("device id  = {}".format(self.current_device_id))

            if self.current_user_action == UserAction.BORROW:
                self.device_db_service.borrow_device(self.current_device_id, self.current_device_name, self.current_student_id)
            elif self.current_user_action == UserAction.RETURN:
                self.device_db_service.return_device(self.current_device_id)

            logging.debug("Devices = {}".format(self.device_db_service.get_all_devices()))
            self.ui.output_label.setStyleSheet("font-size:16pt; color:#ffffff; background-color:#156082;")
            self.ui.output_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.ui.output_label_2.setAlignment(Qt.AlignmentFlag.AlignCenter)

            if self.current_user_action == UserAction.BORROW:
                self.ui.output_label.setText("Device: " + str(self.current_device_name) + "\n" + "Borrowed to: " + str(self.current_student_name))
                self.ui.output_label_2.setText("Device borrowed\nsuccessfully")
            elif self.current_user_action == UserAction.RETURN:
                self.ui.output_label.setText("Device: " + str(self.current_device_name))
                self.ui.output_label_2.setText("Device returned\nsuccessfully")
            self.device_db_service.refresh_connection()
        except Exception as e:
            logging.error(f"Error processing confirm button click: {e}")
            self.show_error_message("Error", f"An error occurred while processing the action: {e}")

    def back_button_1_clicked(self):
        """
        @brief Slot for back button click event on page 3.

        Returns to the student card scanning page or admin page based on user action.
        """
        logging.info("Back button 1 clicked")
        if self.current_user_action == UserAction.ADMIN:
            self.ui.stackedWidget.setCurrentWidget(self.ui.page_admin)
        else:
            self.ui.stackedWidget.setCurrentWidget(self.ui.page_2)
        self.start_nfc_scanner()
        self.current_scan_mode = ScanMode.NFC

    ####################### PAGE 4 - Display output  ############################
    def display_student_name(self, uid):
        """
        @brief Displays the student's name after scanning the NFC card.

        Retrieves the student's information from the database and updates the UI.

        @param uid The UID from the scanned NFC card.
        """
        try:
            logging.info(f"Attempting to display student name for UID: {uid}")
            
            self.ui.matriculation_label.setStyleSheet("font-size:16pt; color:#ffffff; background-color:#156082;")
            self.ui.matriculation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Retrieve student information from the database
            self.current_student_name = self.student_db_service.get_name_from_nfc_uid(uid)
            matriculation_number = self.student_db_service.get_matriculation_number_from_nfc_uid(uid)
            self.current_student_id = self.student_db_service.get_id_from_matriculation_number(matriculation_number)
            
            logging.info(f"Retrieved student name: {self.current_student_name}, Matriculation number: {matriculation_number}, Student ID: {self.current_student_id}")
            
            if self.current_student_name is None:
                self.ui.confirm_button_1.setEnabled(False)
                self.show_student_alert()
                logging.warning("Student name not found in the database.")
            else:
                self.ui.confirm_button.setEnabled(True)
            
            self.ui.matriculation_label.setText("Student Name: " + str(self.current_student_name) + "\n" + "Matriculation number: " + str(matriculation_number))
        except Exception as e:
            logging.error(f"Error displaying student name: {e}")
            self.show_error_message("Error", f"An error occurred while displaying the student name: {e}")

    def display_device_name(self, device_qr_code):
        """
        @brief Displays the device's name after scanning the QR code.

        Retrieves the device's information from the database and updates the UI.

        @param device_qr_code The QR code data from the scanned device.
        """
        try:
            logging.info("device_name = {}".format(device_qr_code))
            device_name = self.device_db_service.get_device_name_from_qr_code(device_qr_code)
            self.current_device_id = self.device_db_service.get_id_from_device_name(device_name)
            device_borrowed_status = self.device_db_service.get_is_borrowed_status_by_device_id(self.current_device_id)

            if device_borrowed_status and self.current_user_action == UserAction.BORROW:
                self.ui.confirm_button_1.setEnabled(False)
                self.show_error_message("Error", "Device is already borrowed.")
            else:      
                if device_name is None:
                    self.ui.confirm_button_1.setEnabled(False)
                    self.show_device_alert()
                else:
                    self.ui.confirm_button_1.setEnabled(True)
                self.ui.device_label.setStyleSheet("font-size:16pt; color:#ffffff; background-color:#156082;")
                self.ui.device_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.ui.device_label.setText("Device name: " + str(device_name))
                self.current_device_name = device_name
        except Exception as e:
            logging.error(f"Error displaying device name: {e}")
            self.show_error_message("Error", f"An error occurred while displaying the device name: {e}")

    def back_button_2_clicked(self):    	
        """
        @brief Slot for back button click event on page 4.

        Returns to the device scanning page.
        """
        logging.info("Back button 2 clicked")
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_3) 
        self.current_scan_mode = ScanMode.QR_CODE

    def home_button_clicked(self):
        """
        @brief Slot for home button click event.

        Returns to the start page.
        """
        logging.info("Home button clicked")
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_1)

    ####################### PAGE 5 - Admin page  ################################
    def admin_button_clicked(self):
        """
        @brief Slot for admin button click event.

        Clears the password input and transitions to the password input page.
        """
        self.password_input.clear()
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_password)

    def admin_submit_button_clicked(self):
        """
        @brief Slot for admin submit button click event.

        Checks the entered password and proceeds if correct.
        """
        # Check if password is correct
        self.set_user_action(UserAction.ADMIN)
        entered_password = self.password_input.text()
        self.password_checker.check_password(entered_password)

    def on_password_verified(self):
        """
        @brief Callback when the password is verified.

        Transitions to the admin functions page.
        """
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_admin)

    def on_password_failed(self):
        """
        @brief Callback when the password verification fails.

        Displays an incorrect password alert.
        """
        self.create_msg_box("Incorrect Password",
        "The password you entered is incorrect.")

    def deactivate_alarm_clicked(self):
        """
        @brief Slot for deactivate alarm button click event.

        Sends a command to deactivate the alarm.
        """
        self.current_admin_action = AdminAction.DEACTIVATE
        logging.info("Deactivating alarm...")
        self.mqtt_gui_services.send_deactivation_command()

    #################################   Utilities ###############################
    def set_user_action(self, action):
        """
        @brief Sets the current user action.

        @param action The action to set (UserAction).
        """
        self.current_user_action = action
        logging.info(f"Action set to {action}")

    def _setup_virtual_numeric_keyboard(self):
        """
        @brief Sets up the virtual numeric keyboard for password input.

        Initializes and configures the virtual keyboard widget.
        """
        # Replace the password_input with CustomLineEdit
        self.password_input = CustomLineEdit(self)
        self.password_input.setStyleSheet("""
            QLineEdit {
                background-color: #333333;
                color: #FFFFFF;
                border-radius: 5px;
                font-size: 18px;
                padding: 10px;
            }
        """)
        # Set the QLineEdit to be a password field
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.keyboard = VirtualKeyboard(self.password_input, "numeric")
        self.password_input.keyboard = self.keyboard
        self.ui.password_layout.addWidget(self.password_input)
        self.ui.password_layout.addWidget(self.keyboard)
        self.keyboard.hide()  # Hide keyboard initially

    def show_alarm_alert(self):
        """
        @brief Displays an alert when the alarm is triggered.

        Creates and shows a message box alerting the user that the alarm has been triggered.
        """
        if self.msg_box is None or not self.msg_box.isVisible():
            self.create_msg_box(
                "Alert",
                "The Alarm has been triggered!\n\nPlease contact the admin to deactivate the alarm."
            )
        else:
            self.msg_box.show()  # Show the existing message box if it's not closed

    def show_device_alert(self):
        """
        @brief Displays an alert when the device is not found.

        Creates and shows a message box informing the user that the device was not found.
        """
        if self.msg_box is None or not self.msg_box.isVisible():
            self.create_msg_box(
                "Device not found",
                "The device was not found in the database."
            )
        else:
            self.msg_box.show()
    
    def show_student_alert(self):
        """
        @brief Displays an alert when the student is not found.

        Creates and shows a message box informing the user that the student was not found.
        """
        if self.msg_box is None or not self.msg_box.isVisible():
            self.create_msg_box(
                "Student not found",
                "The student was not found in the database."
            )
        else:
            self.msg_box.show()

    def show_error_message(self, title, message):
        """
        @brief Displays an error message box.
        @param title The title of the message box.
        @param message The message to display.
        """
        self.create_msg_box(title, message)

    def create_msg_box(self, windowTitle, text):
        """
        @brief Creates a message box with the specified title and text.

        Configures and displays a QMessageBox with custom styles.

        @param windowTitle The title of the message box.
        @param text The text content of the message box.
        """
        self.msg_box = QMessageBox(self)  # Create the message box and store the reference
        self.msg_box.setWindowTitle(windowTitle)
        self.msg_box.setText(text)
        self.msg_box.setIcon(QMessageBox.Icon.Warning) 
        self.msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        self.msg_box.setStyleSheet("""
            QMessageBox {
                background-color: black;
            }
            QMessageBox QLabel {
                color: red;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-size: 18px;
                padding: 20px;
                font-weight: bold;
            }
            QMessageBox QPushButton {
                background-color: red;
                color: white;
                font-weight: bold;
                padding: 10px;
                font-size: 16px;
                border-radius: 10px;
            }
        """)
        self.msg_box.exec()

    def start_nfc_scanner(self):
        """
        @brief Starts the NFC scanner service.

        Resets and starts the NFC service to scan for smart cards.
        """
        self.nfc_service.reset()
        self.nfc_service.start()

    def stop_nfc_scanner(self):
        """
        @brief Stops the NFC scanner service.

        Stops the NFC service and waits for it to finish.
        """
        self.nfc_service.stop()
        self.nfc_service.wait()

    def keyPressEvent(self, event):
        """
        @brief Handles key press events.

        Processes key events for NFC and QR code scanning modes.

        @param event The key event.
        """
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            key = event.text()
            if self.current_scan_mode == ScanMode.NFC:
                # TODO: Handle NFC key input
                pass
            elif self.current_scan_mode == ScanMode.QR_CODE:
                self.qr_code_scanner.scan_qr_code(key)
    
    def reset_device_student_details(self):
        """
        @brief Resets the current device and student details.

        Clears the current device and student IDs and names, and resets the UI labels.
        """
        self.current_device_id = None
        self.current_device_name = None
        self.current_student_id = None
        self.current_student_name = None
        self._reset_label(self.ui.matriculation_label, "Student Name: None \nMatriculation number: None")
        self._reset_label(self.ui.device_label, "Device name: None")

    def _reset_label(self, label, text):
        """
        @brief Resets a UI label to the specified text and style.

        @param label The QLabel to reset.
        @param text The text to set on the label.
        """
        label.setStyleSheet("font-size:16pt; color:#ffffff; background-color:#156082;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setText(text)

    def disable_confirm_button(self):
        """
        @brief Disables the confirm buttons on the UI.

        Disables the confirm buttons to prevent invalid actions.
        """
        self.ui.confirm_button.setEnabled(False)
        self.ui.confirm_button_1.setEnabled(False)
