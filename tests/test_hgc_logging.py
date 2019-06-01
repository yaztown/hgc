'''
Created on Friday 31/05/2019

@author: yaztown
'''

import unittest
from hgc_logging import logger_helper
import logging

class TestLoggerHelper(unittest.TestCase):
    '''
    TestCase for the hgc_logging package
    '''
    def test_get_logger_without_params(self):
        logger = logger_helper.get_logger()
        self.assertIsInstance(logger, logging.Logger, 'get_logger() failed')
    
    def test_get_logger_with_existing_log_dir_params(self):
        import os
        temp_path = os.path.abspath(__file__)
        temp_path = os.path.dirname(temp_path)
        temp_path = os.path.join(temp_path, 'temp_log')
        os.mkdir(temp_path)
        logger = logger_helper.get_logger(name='test_get_logger_with_existing_log_dir_params', log_dir=temp_path)
        file_handler = logger.handlers[1]
        file_handler_path = os.path.dirname(file_handler.baseFilename)
        os.remove(file_handler.baseFilename)
        os.rmdir(temp_path)
        self.assertEqual(file_handler_path, temp_path, 'get_logger(log_dir=???) Error')

    def test_get_logger_with_nonexisting_log_dir_params(self):
        import os
        temp_path = os.path.abspath(__file__)
        temp_path = os.path.dirname(temp_path)
        temp_path = os.path.join(temp_path, 'temp_log')
        
        with self.assertRaises(FileNotFoundError, msg='Didn\'t raise an FileNotFoundError'):
            logger = logger_helper.get_logger(name='test_get_logger_with_nonexisting_log_dir_params', log_dir=temp_path)

    def test_get_logger_log_file_params(self):
        import os
        
        temp_path = os.path.abspath(__file__)
        temp_path = os.path.dirname(temp_path)
        temp_path = os.path.join(temp_path, 'temp_log')
        
        log_file = 'temp_log_file.log'
        file_path = os.path.join(temp_path, log_file)
        
        os.mkdir(temp_path)
        
        logger = logger_helper.get_logger(name='test_get_logger_with_nonexisting_log_file_params', log_dir=temp_path,log_file=log_file)
#         logger.info('from test_get_logger_with_nonexisting_log_file_params()')
        
        file_exists = os.path.exists(file_path)
        
        os.remove(file_path)
        os.rmdir(temp_path)
        
        self.assertTrue(file_exists, msg='log file was not created.')
#         with self.assertRaises(FileNotFoundError):
    
    def test_get_file_handler(self):
        pass