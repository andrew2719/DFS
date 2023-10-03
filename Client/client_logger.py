import logging
from settings import CLIENT_LOG

def setup_logger():
    logger = logging.getLogger('client_logger')
    logger.setLevel(logging.DEBUG)



    # File handler
    file_handler = logging.FileHandler(CLIENT_LOG)
    file_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)

    # Console handler (optional)
    console_handler = logging.StreamHandler()
    console_format = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    return logger

client_logger = setup_logger()

