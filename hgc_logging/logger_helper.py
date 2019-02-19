# logging_example.py

import logging

file_name='hgc.log'

def get_file_handler(level=logging.DEBUG):
    # Create handlers
    f_handler = logging.FileHandler(file_name)
    f_handler.setLevel(level)
    
    # Create formatters and add it to handlers
    f_format = logging.Formatter('%(asctime)s - %(threadName)s - %(levelname)s - %(message)s')
    f_handler.setFormatter(f_format)
    return f_handler

def get_logger(name, level=logging.DEBUG):
    # Create a custom logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    # Add handlers to the logger
    logger.addHandler(get_file_handler())
    return logger


# example
if __name__ == '__main__':
    logger = get_logger(__name__)
    
    logger.debug('This is a debug')
    logger.info('This is an info')
    logger.warning('This is a warning')
    logger.error('This is an error')
    logger.critical('This is critical')
