"""Define a Comm for the bot"""
from __future__ import annotations

import traceback
from ipykernel.comm import Comm

from .chat_instance import ChatInstance
from .message import MessageContext


class KernelComm:
    """Comm handler"""

    def __init__(self, shell=None, loader="base"):
        self.shell = shell
        self.name = "newton.comm"
        self.comm = None

        self.chat_instances = {
            "base": ChatInstance(self, "base", loader)
        }

    def register(self):
        """Registers comm"""
        self.comm = Comm(self.name)
        self.comm.on_msg(self.receive)
        self.chat_instances["base"].sync_chat("init")

    def receive(self, msg):
        """Receives requests"""
        data = msg["content"]["data"]
        try:
            instance = data["instance"]
            instances = self.chat_instances.values()
            if instance != "<all>":
                instances = [self.chat_instances.get(instance, None)]
            for chat_instance in instances:
                chat_instance.receive(data)
        except Exception:  # pylint: disable=broad-except
            print(traceback.format_exc())
            self.chat_instances["base"].send({
                "operation": "error",
                "command": data.get("operation", "<operation undefined>"),
                "message": traceback.format_exc(),
            })

    def reply(self, text, type_="bot", reply=None, instance="base"):
        """Replies message to user"""
        message = MessageContext.create_message(text, type_, reply)
        self.chat_instances[instance].reply_message(message)
