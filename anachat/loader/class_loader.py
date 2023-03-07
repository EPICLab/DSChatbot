"""Defines class loader"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..comm.kernelcomm import KernelComm



def class_loader(cls):
    """Returns class loader"""
    class ClassLoader:
        """Loads the core chatbot module from a class"""

        def __init__(self, comm: KernelComm):
            # pylint: disable=unused-argument
            self.current_core = cls()

        def current(self):
            """Returns current Bot"""
            return self.current_core
    return ClassLoader
