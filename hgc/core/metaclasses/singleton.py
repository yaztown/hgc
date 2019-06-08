'''
Created on Saturday 08/06/2019

@author: yaztown
'''

class Singleton(type):
    """Metaclass providing a singleton instance"""
    _instances = {}
    
    def __call__(self, *args, **kwargs):
        if self not in self._instances:
            self._instances[self] = super(Singleton, self).__call__(*args, **kwargs)
        return self._instances[self]
