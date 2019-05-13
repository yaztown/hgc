'''
Created on Tuesday 03/07/2018

@author: yaztown
'''
'''
Created on Monday 02/07/2018

file: base_threads.py

@author: yaztown
'''

#device_control_base

from .class_instance_registry import MetaInstanceRegistry
from time import sleep
import threading


DEFAULT_SLEEP_TIME = 2


class BaseThread(threading.Thread, metaclass=MetaInstanceRegistry):
    '''
    class: BaseThread
    
    (Development of this class has Raspberry Pi in mind.)
    '''
    def __init__(self, loop_sleep_time=DEFAULT_SLEEP_TIME, *args, **kwargs):
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
        
        # Flag to exit thread's runloop
        self._exit_loop = False
        
        # Flag to pause thread
        self._paused = False
        
        # Explicitly using Lock over RLock since the use of self._paused
        # break reentrancy anyway, and I believe using Lock could allow
        # one thread to pause the worker, while another resumes; haven't
        # checked if Condition imposes additional limitations that would 
        # prevent that. In Python 2, use of Lock instead of RLock also
        # boosts performance.
        self._pause_condition = threading.Condition(threading.Lock())
        self._pause_condition.acquire_count = 0
    
    def __work__(self):
        '''
        This method should be implemented in subclasses and is where the threads
        repeating process goes (without the loop since it is in the run() method.
        '''
        raise NotImplementedError('must implement in subclasses')
    
    # This thread's control methods
    def run(self):
        # TODO: Add a run_setup() somewhere before the loop
        while not self._exit_loop:
            with self._pause_condition:
                # TODO: Can I change this while to if?!
                while self._paused:
                    self._pause_condition.wait()
                # thread should do the work if not paused
                self.__work__()
            sleep(self.loop_sleep_time)
    
    def pause(self):
        '''
        This will pause the thread until it is resumed by calling the resume() method
        '''
        if not self._paused:
            self._paused = True
            # If in sleep, we acquire immediately, otherwise we wait for thread
            # to release condition. In race, worker will still see self._paused
            # and begin waiting until it's set back to False
            if self.is_alive():
                # Notify so thread will wake after lock released
                self._pause_condition.acquire()
                self._pause_condition.acquire_count += 1
    
    def resume(self):
        '''
        This will resume the thread after being paused.
        Note: It will not resume a stopped thread.
        '''
        if self._paused:
            self._paused = False
            if self.is_alive() and self._pause_condition.acquire_count > 0:
                # Notify so thread will wake after lock released
                self._pause_condition.notify()
                # Now we release the lock
                self._pause_condition.release()
                self._pause_condition.acquire_count -= 1
    
    def stop(self):
        '''
        This will stop the thread perminently
        similar to: kill()
        '''
        self._exit_loop = True
        if self.is_alive() and self._paused:
            self.resume()
    
    def kill(self):
        '''
        This will stop the thread perminently
        similar to: stop()
        '''
        self.stop()
    
    @property
    def _serialized_(self):
        return {
            'loop_sleep_time': self.loop_sleep_time,
            'name': self.name,
            'daemon': self.daemon,
            'is_alive': self.is_alive(),
            '_started': self._started.is_set(),
            '_exit_loop': self._exit_loop,
            '_paused': self._paused,
            '_is_stopped': self._is_stopped,
        }
