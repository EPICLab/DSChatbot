"""Defines base loader"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..comm.kernelcomm import KernelComm


class BaseLoader:
    """Loads the core chatbot module"""

    def __init__(self, comm: KernelComm):
        # pylint: disable=unused-argument
        # pylint: disable=import-outside-toplevel
        from .. import core
        self.core = core

    def current(self):
        """Returns current Bot"""
        return self.core.CURRENT
