from PyQt6.QtCore import QObject, pyqtSignal

class PasswordChecker(QObject):
    """
    @class PasswordChecker
    @brief A class to handle password verification.
    """
    password_verified = pyqtSignal()
    """ @brief Signal emitted when the password is verified successfully. """

    password_failed = pyqtSignal()
    """ @brief Signal emitted when the password verification fails. """

    def __init__(self, admin_password, parent=None):
        """
        @brief Constructor for PasswordChecker.
        @param admin_password The admin password to verify against.
        @param parent The parent QObject, if any.
        """
        super().__init__(parent)
        self.admin_password = admin_password

    def check_password(self, entered_password):
        """
        @brief Checks the entered password against the admin password.
        @param entered_password The password entered by the user.
        """
        if entered_password == self.admin_password:
            self.password_verified.emit()
        else:
            self.password_failed.emit()