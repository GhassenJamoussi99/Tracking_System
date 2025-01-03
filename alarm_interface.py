import logging_config
from application_layer.alarm_pi.alarm_service import AlarmService

############################## Setup Logger #############################
logging_config.setup_logging()
#########################################################################

if __name__ == "__main__":
    service = AlarmService()
    service.start()

