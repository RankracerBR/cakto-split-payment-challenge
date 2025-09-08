import logging


def setup_logging():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('split_payments')
    
    # Add file handler for compliance logs
    file_handler = logging.FileHandler('/var/log/split_payments.log')
    file_handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    
    return logger
