"""Define a Comm for the bot"""
from __future__ import annotations

import traceback
from ipykernel.comm import Comm

from ..loader import LOADERS
from .chat_instance import ChatInstance
from .message import MessageContext


class KernelComm:
    """Comm handler"""

    def __init__(self, shell=None, mode="newton"):
        self.shell = shell
        self.name = "newton.comm"
        self.comm = None

        self.chat_instances = {
            "base": ChatInstance(self, "base", mode)
        }

    def register(self):
        """Registers comm"""
        self.comm = Comm(self.name)
        self.comm.on_msg(self.receive)
        self.sync_meta()
        self.chat_instances["base"].sync_chat("init")

    def sync_meta(self):
        """Sends list of loaders and instances to client"""
        self.comm.send({
            "operation": "sync-meta",
            "instance": "<meta>",
            "loaders": {
                key: value.config()
                for key, value in LOADERS.items()
            },
            "instances": {
                key: value.mode
                for key, value in self.chat_instances.items()
            },
        })

    def receive(self, msg):
        """Receives requests"""
        data = msg["content"]["data"]
        try:
            instance = data["instance"]
            if instance == "<meta>":
                operation = data.get("operation", "")
                if operation == "new-instance":
                    chat_instance = self.chat_instances[data["name"]] = ChatInstance(
                        self, data["name"], data.get("mode", "base"), data.get("data", {})
                    )
                    chat_instance.sync_chat("init")
                    self.sync_meta()
                elif operation == "refresh":
                    self.sync_meta()
                elif operation == "remove-instance":
                    del self.chat_instances[data["name"]]
                    self.sync_meta()
                return
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
