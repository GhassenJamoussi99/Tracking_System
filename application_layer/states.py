from enum import Enum

class ScanMode(Enum):
    """
    @enum ScanMode
    @brief Enumeration for different scanning modes.
    """
    NFC = "NFC"          
    QR_CODE = "QR_CODE" 

class UserAction(Enum):
    """
    @enum UserAction
    @brief Enumeration for different user actions.
    """
    BORROW = "borrow"   
    RETURN = "return"    
    ADMIN = "admin"      
    
class AdminAction(Enum):
    """
    @enum AdminAction
    @brief Enumeration for different admin actions.
    """
    #Can be incremented in the future
    DEACTIVATE = "deactivate"