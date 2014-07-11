import inspect
from . import log

class Dispatcher(object):

    def __init__(self):
        self.events = {}

    def add_callback(self, name, callback):
        if not name in self.events:
            self.events[name] = []
        self.events[name].append(callback)
        
    def remove_callback(self, name, callback):
        if not name in self.events:
            return
        self.events[name].remove(callback)
        
    def fire(self, name, data=None):
        if not name in self.events:
            return
        for callback in self.events[name]:
            if len(inspect.getargspec(callback).args):
                callback(data)
            else:
                callback()
