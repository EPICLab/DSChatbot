"""Define a Comm for Ana"""
from __future__ import annotations
from typing import TYPE_CHECKING

import traceback
from collections import defaultdict, namedtuple
from ipykernel.comm import Comm

from .message import MessageContext
from .core_loader import BaseLoader
from .message import KernelProcess

OptionsActions = namedtuple("OptionsActions", ['last', 'all'])


if TYPE_CHECKING:
    from .message import IChatMessage


def apply_partial(original: dict, update: dict):
    """Apply nested changes to original dict"""
    for key, value in update.items():
        if isinstance(value, dict):
            apply_partial(original[key], value)
        else:
            original[key] = value


class AnaComm:
    """Ana comm hadler"""

    def __init__(self, shell=None, core_loader=BaseLoader):
        self.shell = shell
        self.memory = defaultdict(lambda: None)
        self.name = "anachat.comm"
        self.comm = None
        self.core_loader = core_loader(self)

        self.history = [MessageContext.create_message(
            ("Hello, I am Newton, an assistant that can help you with machine learning. "
             "You can ask me questions at any given time and go back to previous questions too. "
             "How can I help you?"),
            "bot"
        )]
        self.message_map = {
            self.history[-1]['id']: self.history[-1]
        }
        self.instance_config = {
            "process_in_kernel": True,
            "enable_auto_complete": True,
            "enable_auto_loading": False,
            "loading": False,

            "show_replied": False,
            "show_index": False,
            "show_time": True,
            "show_build_messages": True,
            "show_kernel_messages": True,
        }
        self.checkpoints = {}

    @property
    def core(self):
        """Returns current AnaCore"""
        return self.core_loader.core.CURRENT

    def history_message(self, operation, instance="base"):
        """Returns message with history and general config"""
        return {
            "instance": instance,
            "operation": operation,
            "history": self.history,
            "config": self.instance_config,
        }

    def register(self):
        """Registers comm"""
        self.comm = Comm(self.name)
        self.comm.on_msg(self.receive)
        self.send(self.history_message("init"))

    def receive(self, msg):
        """Receives requests"""
        data = msg["content"]["data"]
        try:
            operation = data["operation"]
            instance = data["instance"]
            if operation == "message":
                self.receive_message(instance, data.get("message"))
            elif operation == "refresh":
                self.core.refresh(self, instance)
            elif operation == "query":
                self.receive_query(
                    instance,
                    data.get('type'),
                    data.get('requestId'),
                    data.get('query')
                )
            elif operation == "config":
                key = data["key"]
                value = data["value"]
                if data["_mode"] == "update" or key not in self.instance_config:
                    self.instance_config[key] = value
                self.send({
                    "instance": instance,
                    "operation": "updateconfig",
                    "config": {key: self.instance_config[key]},
                })
            elif operation == "syncmessage":
                partial_message = data["message"]
                message = self.message_map[partial_message["id"]]
                apply_partial(message, partial_message)
                self.send({
                    "instance": instance,
                    "operation": "updatemessage",
                    "message": message,
                })
        except Exception:  # pylint: disable=broad-except
            print(traceback.format_exc())
            self.send({
                "instance": instance,
                "operation": "error",
                "command": operation,
                "message": traceback.format_exc(),
            })

    def receive_message(self, instance: str, message: IChatMessage):
        """Receives message from user"""
        self.history.append(message)
        self.message_map[message['id']] = message
        self.send({
            "instance": instance,
            "operation": "reply",
            "message": message
        })
        process_message = (
            message.get('kernelProcess') == KernelProcess.PROCESS
            and self.instance_config["process_in_kernel"]
            or message.get('kernelProcess') == KernelProcess.FORCE
        )
        if process_message:
            context = MessageContext(self, message, instance)
            self.core.process_message(context)

    def receive_query(self, instance, query_type, request_id, query):
        """Receives query from user"""
        if self.instance_config["enable_auto_complete"]:
            self.core.process_query(self, instance, query_type, request_id, query)
        else:
            self.send({
                "instance": instance,
                "operation": "subjects",
                "responseId": request_id,
                "items": [],
            })

    def send(self, data):
        """Receives send results"""
        self.comm.send(data)

    def reply(self, text, type_="bot", reply=None, instance="base"):
        """Replies message to user"""
        message = MessageContext.create_message(text, type_, reply)
        self.reply_message(instance, message)

    def reply_message(self, instance: str, message: IChatMessage):
        """Replies IChatMessage to user"""
        self.history.append(message)
        self.message_map[message['id']] = message
        self.send({
            "instance": instance,
            "operation": "reply",
            "message": message
        })
