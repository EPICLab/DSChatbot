"""Defines base loader"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..comm.kernelcomm import KernelComm


class NewtonLoader:
    """Loads the newton chatbot module"""

    def __init__(self, comm: KernelComm):
        # pylint: disable=unused-argument
        # pylint: disable=import-outside-toplevel
        from ..bots import newton
        self.core = newton

    def current(self):
        """Returns current Bot"""
        return self.core.CURRENT

    @classmethod
    def config(cls):
        """Returns available bot config"""
        from ..bots.newton import NewtonBot
        return NewtonBot.config()
