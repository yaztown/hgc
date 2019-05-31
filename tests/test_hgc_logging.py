'''
Created on Friday 31/05/2019

@author: yaztown
'''

import unittest
from hgc_logging import logger_helper
import logging

class TestLoggerHelper(unittest.TestCase):
    def test_get_logger_without_params(self):
        logger = logger_helper.get_logger()
        self.assertIsInstance(logger, logging.Logger, 'get_logger() failed')
