'''
Created on Sunday 10/03/2019

@author: yaztown
'''

import weakref

class MetaInstanceRegistry(type):
    """Metaclass providing an instance registry"""
    def __init__(cls, name, bases, attrs):
        # Create class
        super(MetaInstanceRegistry, cls).__init__(name, bases, attrs)
        
        # Initialize fresh instance storage
        cls._instances = weakref.WeakSet()
    
    def __call__(cls, *args, **kwargs):
        # Create instance (calls __init__ and __new__ methods)
        inst = super(MetaInstanceRegistry, cls).__call__(*args, **kwargs)
        
        # Store weak reference to instance. WeakSet will automatically remove
        # references to objects that have been garbage collected
        cls._instances.add(inst)
        
        return inst
    
    def _get_instances(cls, recursive=False):
        """Get all instances of this class in the registry. If recursive=True
        search subclasses recursively"""
        instances = list(cls._instances)
        if recursive:
            for Child in cls.__subclasses__():
                instances += Child._get_instances(recursive=recursive)
        
        # Remove duplicates from multiple inheritance.
        return list(set(instances))
