'''
Created on Monday 27/05/2019

@author: yaztown
'''
from .base_exceptions import ThreadExitException
import signal

def shutdown_routine(signum, frame):
    sig = signal._int_to_enum(signum,signal.Signals)
    print('\nReceived {}.'.format(sig.name))
    raise ThreadExitException()

def register_exit_signal_handler():
    signal.signal(signal.SIGTERM, shutdown_routine)
    signal.signal(signal.SIGINT, shutdown_routine)