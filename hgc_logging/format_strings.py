'''
Created on Saturday 25/05/2019

@author: yaztown
'''

fmt_debug = '''----------
%(name)s
%(asctime)s - %(levelname)-8s %(threadName)-20s %(module)s -> %(funcName)s @ %(lineno)d:
%(message)s
----------'''

fmt_info = '''----------
%(name)s
%(asctime)s - %(levelname)-8s - %(threadName)s:
%(message)s
----------'''

fmt_date_small = '%m-%d %H:%M:%S'


fmt_simple_debug = '%(asctime)s %(levelname)-8s %(threadName)-20s %(module)s -> %(funcName)s @ %(lineno)d: %(message)s'

fmt_simpole_info = '%(asctime)s %(levelname)-8s %(threadName)s: %(message)s'

