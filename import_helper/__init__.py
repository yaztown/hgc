'''
import_helper includes function to retrieve classes from their modules
'''

import importlib
import logging

def class_from_module_str_and_class_str(module_name, class_name):
    try:
        module_ = importlib.import_module(module_name)
        try:
            class_ = getattr(module_, class_name)()
        except AttributeError:
            logging.error('Class does not exist')
    except ImportError:
        logging.error('Module does not exist')
    return class_ or None

def class_from_str(module_, class_name):
    try:
        class_ = getattr(module_, class_name)()
    except AttributeError:
        logging.error('Class does not exist')
    return class_ or None

