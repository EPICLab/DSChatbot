"""Provides class related to handling urls"""

from ...comm.context import MessageContext
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
