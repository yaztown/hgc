'''
Created on Monday 27/05/2019

@author: yaztown
'''

class ThreadExitException(Exception):
    """
    Custom exception which is used to trigger the clean exit
    of all running threads and the main program.
    """
    pass