"""Provides class related to handling urls"""
from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ...comm.message import MessageContext
    from ..states.state import StateDefinition


class WozHandler:
    """Handler that does not do anything for wizard of woz"""
    # pylint: disable=too-few-public-methods

    def process_message(self, context: MessageContext) -> StateDefinition:
        """Processes user message"""
        # pylint: disable=no-self-use
        if context.text.startswith(">"):
            return True
        return None
