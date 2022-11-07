"""Utility functions for handlers"""

from abc import abstractmethod
import os

class HandlerWithPaths:
    """Handle changes on loaded data files"""

    def __init__(self):
        self.paths = {}
        self.reload()

    def reload(self):
        """Reloads paths"""
        self.paths = {}
        self.inner_reload()

    def check_updates(self):
        """Checks if any of the monitored files has changed"""
        for filepath, oldtime in self.paths.items():
            if oldtime != self.getmtime(filepath):
                self.reload()
                break

    def process_message(self, comm, text, reply_to, replying_to):
        """Processes users message"""
        self.check_updates()
        return self.inner_process_message(comm, text, reply_to, replying_to)

    def getmtime(self, path):
        """Returns the mofication time of a file"""
        # pylint: disable=no-self-use
        try:
            return os.path.getmtime(path)
        except OSError:
            return None

    @abstractmethod
    def inner_reload(self):
        """Defines how to reload paths for subclasses"""

    @abstractmethod
    def inner_process_message(self, comm, text, reply_to, replying_to):
        """Defines how to process messages for subclasses"""
