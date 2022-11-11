"""Defines a MessageContext"""
from __future__ import annotations
from typing import TYPE_CHECKING

from dataclasses import dataclass


if TYPE_CHECKING:
    from typing import TypedDict, List
    from .anacomm import AnaComm

    class Option(TypedDict, total=False):
        """Defines an Option for a list of options"""
        key: str
        label: str


@dataclass
class MessageContext:
    """Represents a message context"""

    comm: AnaComm
    text: str
    reply_to: str | None = None
    replying_to: str | None = None

    def reply(self, message: str | List[Option], type_: str="bot"):
        """Reply indicating the reply_to field"""
        self.comm.reply(message, type_=type_, reply=self.reply_to)
