'''
Created on Monday 02/07/2018

file: base_threads.py

@author: yaztown
'''

#device_control_base

from hgc.core.metaclasses import MetaInstanceRegistry
from uuid import uuid4
from time import sleep
from hgc_logging import get_logger
import threading

DEFAULT_SLEEP_TIME = 2

logger = get_logger()

class BaseThread(threading.Thread, metaclass=MetaInstanceRegistry):
    '''
    class: BaseThread
    
    (Development of this class has Raspberry Pi in mind.)
    '''
    def __init__(self, loop_sleep_time=DEFAULT_SLEEP_TIME, uuid=uuid4().hex, *args, **kwargs):
        '''
        loop_sleep_time: is the time for the thread to sleep before looping again; default = DEFAULT_SLEEP_TIME seconds.
        name           : is a general name for the thread.
        group          : should be None; reserved for future extension when a ThreadGroup
                         class is implemented.
        target         : is the callable object to be invoked by the run()
                         method. Defaults to None, meaning nothing is called.
        args           : is the argument tuple for the target invocation. Defaults to ().
        kwargs         : is a dictionary of keyword arguments for the target
                         invocation. Defaults to {}.
        daemon         : is the flag to indicate that the thread should run in daemon mode
        '''
#         super().__init__(name=name, group=group, target=target, args=args, kwargs=kwargs, daemon=daemon)
        super().__init__(*args, **kwargs)
        self.loop_sleep_time = loop_sleep_time
        
        # Check to see if passed uuid is unique to us. 
        if self.__class__._get_instance_by_uuid(uuid) is None:
            self.uuid = uuid
        else:
            self.uuid = uuid4().hex
        
        # Flag to exit thread's runloop
        self._exit_loop = threading.Event()
        
        # Flag to pause thread
        self._paused = threading.Event()
        
        # Explicitly using Lock over RLock since the use of self._paused
        # break reentrancy anyway, and I believe using Lock could allow
        # one thread to pause the worker, while another resumes; haven't
        # checked if Condition imposes additional limitations that would 
        # prevent that. In Python 2, use of Lock instead of RLock also
        # boosts performance.
        self._pause_condition = threading.Condition(threading.Lock())
        self._pause_condition.acquire_count = 0
    
    def _setup_loop(self):
        '''
        Override this methods to customize work to be done by the thread just before the loop.
        '''
        pass
    
    def __loop__(self):
        '''
        This method should be implemented in subclasses and is where the threads
        repeating process goes (without the while-loop since it is in the run() method.
        '''
        raise NotImplementedError('must implement in subclasses')
    
    # This thread's control methods
    def run(self):
        # TODO: Add a run_setup() somewhere before the loop
        logger.debug('Starting run() on thread: {}'.format(self.name))
        self._setup_loop()
        while not self._exit_loop.is_set():
            with self._pause_condition:
                # TODO: Can I change this while to if?!
                while self._paused.is_set():
                    self._pause_condition.wait()
                # thread should loop if not paused
                self.__loop__()
            sleep(self.loop_sleep_time)
        self.clean_up()
        logger.debug('Exiting thread: {}'.format(self.name))
    
    def pause(self):
        '''
        This will pause the thread until it is resumed by calling the resume() method
        '''
        if not self._paused.is_set():
            self._paused.set()
            logger.debug('Paused thread: {}'.format(self.name))
            # If in sleep, we acquire immediately, otherwise we wait for thread
            # to release condition. In race, worker will still see self._paused
            # and begin waiting until self._paused is cleared
            if self.is_alive():
                # Notify so thread will wake after lock released
                self._pause_condition.acquire()
                self._pause_condition.acquire_count += 1
    
    def resume(self):
        '''
        This will resume the thread after being paused.
        Note: It will not resume a stopped thread.
        '''
        if self._paused.is_set():
            self._paused.clear()
            if self.is_alive() and self._pause_condition.acquire_count > 0:
                # Notify so thread will wake after lock released
                self._pause_condition.notify()
                # Now we release the lock
                self._pause_condition.release()
                self._pause_condition.acquire_count -= 1
            logger.debug('Resumed thread: {}'.format(self.name))
    
    def stop(self):
        '''
        This will stop the thread perminently
        similar to: kill()
        '''
        logger.debug('Stopping thread: {}'.format(self.name))
        self._exit_loop.set()
        if self.is_alive() and self._paused.is_set():
            self.resume()
    
    def kill(self):
        '''
        This will stop the thread perminently
        similar to: stop()
        '''
        self.stop()
    
    def clean_up(self):
        '''
        When overloading, make sure to call the super().clean_up()
        at the end of the implementation.
        '''
        pass
    
    @classmethod
    def _get_instances(cls, recursive=True):
        """Get all instances of this class in the registry. If recursive=True
        search subclasses recursively"""
        instances = list(cls._instances)
        if recursive:
            for Child in cls.__subclasses__():
                instances += Child._get_instances(recursive=recursive)
        
        # Remove duplicates from multiple inheritance.
        return list(set(instances))

    @classmethod
    def _get_instance_by_uuid(cls, uuid=None, recursive=True):
        """Get all instances of this class in the registry.
        If recursive=True search subclasses recursively"""
        instances = cls._get_instances(recursive)
        obj = None
        for inst in instances:
            if inst.uuid == uuid:
                obj = inst
                break
        return obj

    @property
    def _serialized_(self):
        return {
            'uuid': self.uuid,
            'loop_sleep_time': self.loop_sleep_time,
            'name': self.name,
            'daemon': self.daemon,
            'is_alive': self.is_alive(),
            '_started': self._started.is_set(),
            '_exit_loop': self._exit_loop.is_set(),
            '_paused': self._paused.is_set(),
            '_is_stopped': self._is_stopped,
        }
