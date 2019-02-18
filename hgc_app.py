'''
Created on Tuesday 03/07/2018

@author: yaztown
'''

from time import sleep
from hgc import MainLoop, HGC_SETUP, HGC_SETUP_TEST

import logging
#TODO: Centralize the logging elsewhere
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(threadName)-20s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M:%S',
                    filename='log/hgc_app.log.txt',
                    filemode='w'
                    )

def main():
    main_loop = MainLoop(setup_object=HGC_SETUP, name='main_loop', loop_sleep_time=1)
    logging.debug('Starting main_loop')
    main_loop.start()
    
    _exit_loop = False
    
    while not _exit_loop:
        if not main_loop.get_status():
            raise Exception()
        sleep(2)

if __name__ == '__main__':
    main()
