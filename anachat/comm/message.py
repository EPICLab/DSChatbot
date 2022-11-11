"""Defines a MessageContext"""
from __future__ import annotations
from typing import TYPE_CHECKING

import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum


if TYPE_CHECKING:
    from typing import List, TypedDict

    from .anacomm import AnaComm

    class IOptionItem(TypedDict, total=False):
        """Defines an Option for a list of options"""
        key: str
        label: str

    class IChatMessage(TypedDict):
        """Represets a message"""
        id: str
        text: str | List[IOptionItem]
        type: str
        timestamp: int
        reply: str | None
        display: MessageDisplay

        kernelProcess: KernelProcess
        kernelDisplay: MessageDisplay


class MessageDisplay(IntEnum):
    """Represents a message display mode"""
    DEFAULT = 0
    HIDDEN = 1
    SUPERMODE_INPUT = 2


class KernelProcess(IntEnum):
    """Indicates whether or not the kernel should process the message"""
    PREVENT = 0
    PROCESS = 1
    FORCE = 2


@dataclass
class MessageContext:
    """Represents a message context"""

    comm: AnaComm
    original_message: IChatMessage

    @staticmethod
    def create_message(
        text: str | List[IOptionItem],
        type_: str,
        reply: str | None = None,
        display: MessageDisplay = MessageDisplay.DEFAULT
    ) -> IChatMessage:
        """Creates IChatMessage"""
        return {
            "id": str(uuid.uuid4()),
            "text": text,
            "type": type_,
            "timestamp": int(datetime.timestamp(datetime.now())*1000),
            "reply": reply,
            "display": int(display),
            "kernelProcess": int(KernelProcess.PREVENT),
            "kernelDisplay": int(MessageDisplay.DEFAULT),
        }

    @property
    def text(self):
        """Returns original message text"""
        return self.original_message['text']

    def reply(self, message: str | List[IOptionItem], type_: str="bot"):
        """Reply indicating the reply_to field"""
        self.comm.reply_message(self.create_message(
            message,
            type_,
            self.original_message['id'],
            self.original_message['kernelDisplay']
        ))
