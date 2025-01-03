from application_layer.rfid_pi.rfid_service import RFIDService
import logging_config

############################## Setup Logger #############################
logging_config.setup_logging()
#########################################################################

if __name__ == "__main__":
    service = RFIDService()
    service.start()
