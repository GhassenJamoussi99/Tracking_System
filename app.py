from PyQt6 import QtGui
from PyQt6.QtWidgets import QApplication

import logging
import logging_config
import sys

from presentation_layer.views.mainwindow_view import CMainwindowView

############################## Setup Logger #############################
logging_config.setup_logging()
#########################################################################

######################## setup exception handler ########################
logger = logging.getLogger(__name__)

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, 
                           exc_value, 
                           exc_traceback)
        return

    logger.error("Uncaught exception", 
                    exc_info=(exc_type, 
                              exc_value, 
                              exc_traceback))

# Install exception handler
sys.excepthook = handle_exception
#########################################################################

class App(QApplication):
    def __init__(self, sys_argv):
        super(App, self).__init__(sys_argv)
        self.stackwindowView = CMainwindowView()
        screen = QtGui.QGuiApplication.primaryScreen()
        size = screen.size()
        logging.debug(f"Width: {size.width()}, Height: {size.height()}")
        #self.stackwindowView.showFullScreen()
        self.stackwindowView.show()

if __name__ == "__main__":
    #clear logs before starting the program
    open('logs.log', 'w').close() 
    #start Qt application
    app = App(sys.argv)
    sys.exit(app.exec())