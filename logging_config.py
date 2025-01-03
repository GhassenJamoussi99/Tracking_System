import logging

def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(threadName)s, %(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("logs.log"),
            logging.StreamHandler()
        ]
    )
