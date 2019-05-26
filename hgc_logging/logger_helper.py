'''
Created on Saturday 25/05/2019

@author: yaztown
'''

from hgc_logging.format_strings import fmt_debug, fmt_info, fmt_date_small

import logging
import os
app_dirname, _ = os.path.split(os.path.dirname(os.path.abspath(__file__)))
default_log_dirname = os.path.join(app_dirname, 'log')


default_file_name='hgc.log'


def get_console_handler(level=logging.DEBUG):
    # Create handler
    hdl_console = logging.StreamHandler()
    hdl_console.setLevel(level)
    # Create formatters
    formatter_info = logging.Formatter(fmt_info, datefmt=fmt_date_small)
    hdl_console.setFormatter(formatter_info)
    return hdl_console

def get_file_handler(level=logging.DEBUG, log_dir=None, file_name=None):
    if file_name is None:
        file_name = default_file_name
    if log_dir is None:
        log_dir = default_log_dirname
    hdl_file = logging.FileHandler(os.path.join(log_dir, file_name), mode='w')
    hdl_file.setLevel(level)
    # Create formatters
    formatter_debug = logging.Formatter(fmt_debug, datefmt=fmt_date_small)
    hdl_file.setFormatter(formatter_debug)
    return hdl_file

def get_logger(name, level=logging.DEBUG, log_dir=None, file_name=None):
    # Create a custom logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    # Add handlers to the logger
    logger.addHandler(get_console_handler(level))
    logger.addHandler(get_file_handler(level, log_dir, file_name))
    return logger


# example
if __name__ == '__main__':
    logger = get_logger('logger_helper')
    
    logger.debug('This is a debug')
    logger.info('This is an info')
    logger.warning('This is a warning')
    logger.error('This is an error')
    logger.critical('This is critical')
