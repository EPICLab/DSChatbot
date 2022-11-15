"""Provides class related to handling urls"""
from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ...comm.message import MessageContext
    from ..states.state import StateDefinition


class URLHandler:
    """Handler that opens Panel if user types a URL"""
    # pylint: disable=too-few-public-methods

    def process_message(self, context: MessageContext) -> StateDefinition:
        """Processes user message"""
        # pylint: disable=no-self-use
        text = context.text
        if text.startswith("http://") or text.startswith("https://"):
            context.reply(f"####web-panel#:URL View#:{text}")
            return True
        return None
