"""Utility functions for handlers"""
from __future__ import annotations
from typing import TYPE_CHECKING

from abc import abstractmethod
import os


if TYPE_CHECKING:
    from ....comm.message import MessageContext
    from ..states.state import StateDefinition


class HandlerWithPaths:
    """Handle changes on loaded data files"""

    def __init__(self):
        self.paths = {}
        self.reload()

    def reload(self) -> None:
        """Reloads paths"""
        self.paths = {}
        self.inner_reload()

    def check_updates(self) -> None:
        """Checks if any of the monitored files has changed"""
        for filepath, oldtime in self.paths.items():
            if oldtime != self.getmtime(filepath):
                self.reload()
                break

    def process_message(self, context: MessageContext) -> StateDefinition:
        """Processes users message"""
        self.check_updates()
        return self.inner_process_message(context)

    def getmtime(self, path):
        """Returns the mofication time of a file"""
        # pylint: disable=no-self-use
        try:
            return os.path.getmtime(path)
        except OSError:
            return None

    @abstractmethod
    def inner_reload(self) -> None:
        """Defines how to reload paths for subclasses"""

    @abstractmethod
    def inner_process_message(self, context: MessageContext) -> StateDefinition:
        """Defines how to process messages for subclasses"""
