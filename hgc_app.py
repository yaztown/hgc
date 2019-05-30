'''
Created on Tuesday 03/07/2018

@author: yaztown
'''

from time import sleep
from hgc import MainLoop, load_settings_from_file #, HGC_SETTINGS, HGC_SETTINGS_TEST
from base_threads import register_exit_signal_handler, ThreadExitException

import hgc_logging
logger = hgc_logging.get_logger()

def main():
    settings = load_settings_from_file('hgc_settings_minimal.json')
    main_loop = MainLoop(setup_object=settings, name='main_loop', loop_sleep_time=1)
    logger.debug('Starting main_loop')
    register_exit_signal_handler()
    main_loop.start()
    try:
        # Keep the main thread running, otherwise signals are ignored.
        while True:
#             main_loop.get_status()
            sleep(0.5)
 
    except ThreadExitException:
        # Terminate the running threads.
        # Set the shutdown flag on each thread to trigger a clean shutdown of each thread.
        main_loop.stop()
        # Wait for the threads to close...
        main_loop.join()
    logger.debug('Exiting...')
#     
#     while not _exit_loop:
#         if not main_loop.get_status():
#             raise Exception()
#         sleep(2)

if __name__ == '__main__':
    main()
