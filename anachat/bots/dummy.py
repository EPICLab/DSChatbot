"""Defines dummy bot"""
from __future__ import annotations
from typing import TYPE_CHECKING

from ..comm.message import MessageContext 

if TYPE_CHECKING:
    from ..comm.chat_instance import ChatInstance


class DummyBot:
    """Dummy bot that only repeats user messages"""

    def __init__(self):
        self.format_str = "{}, ditto"

    @classmethod
    def config(cls):
        """Defines configuration inputs for bot"""
        return {"format_str": ('str', "{}, ditto")}

    def start(self, instance: ChatInstance, data: dict):
        """Initializes bot"""
        self.format_str = data.get("format_str", self.format_str)
        instance.history.append(MessageContext.create_message(
            ("Hello, I am a dummy bot that repeats messages"),
            "bot"
        ))

    def refresh(self, instance: ChatInstance):
        """Refresh chatbot"""
        # pylint: disable=no-self-use
        instance.sync_chat("refresh")

    def process_message(self, context: MessageContext) -> None:
        """Processes user messages"""
        # pylint: disable=unused-argument
        context.reply(context.text + ", ditto")
        return self

    def process_autocomplete(self, instance: ChatInstance, request_id: int, query: str):
        """Processes user autocomplete query"""
        # pylint: disable=unused-argument
        # pylint: disable=no-self-use
        instance.send({
            "operation": "autocomplete-response",
            "responseId": request_id,
            "items": [],
        })
