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


class AnaComm:
    """Ana comm hadler"""

    def __init__(self, shell=None, core_loader=BaseLoader):
        self.shell = shell
        self.memory = defaultdict(lambda: None)
        self.name = "anachat.comm"
        self.comm = None
        self.core_loader = core_loader(self)

        self.message_processing_enabled = True
        self.query_processing_enabled = True
        self.loading = []
        self.auto_loading = False

        self.history = [MessageContext.create_message(
            ("Hello, I am Newton, an assistant that can help you with machine learning. "
             "You can ask me questions at any given time and go back to previous questions too. "
             "How can I help you?"),
            "bot"
        )]
        self.message_map = {
            self.history[-1]['id']: self.history[-1]
        }
        self.checkpoints = {}

    @property
    def core(self):
        """Returns current AnaCore"""
        return self.core_loader.core.CURRENT

    def history_message(self, operation):
        """Returns message with history and general config"""
        return {
            "operation": operation,
            "history": self.history,
            "message_processing_enabled": self.message_processing_enabled,
            "query_processing_enabled": self.query_processing_enabled,
            "loading": self.loading,
            "auto_loading": self.auto_loading
        }

    def register(self):
        """Registers comm"""
        self.comm = Comm(self.name)
        self.comm.on_msg(self.receive)
        self.send(self.history_message("init"))

    def receive(self, msg):
        """Receives requests"""
        data = msg["content"]["data"]
        operation = data.get("operation", "<undefined>")
        try:
            if operation == "message":
                self.receive_message(data.get("message"))
            elif operation == "refresh":
                self.core.refresh(self)
            elif operation == "query":
                self.receive_query(
                    data.get('type'),
                    data.get('requestId'),
                    data.get('query')
                )
            elif operation == "supermode":
                if (value := data.get("message_processing", None)) is not None:
                    self.message_processing_enabled = value
                if (value := data.get("query_processing", None)) is not None:
                    self.query_processing_enabled = value
                if (value := data.get("loading", None)) is not None:
                    if value is False:
                        self.loading = []
                    else:
                        self.loading.append(value)
                if (value := data.get("remove_loading", None)) is not None:
                    if value is False:
                        self.loading = []
                    for index, message in enumerate(self.history):
                        if message['id'] == value and index in self.loading:
                            self.loading.remove(index)
                if (value := data.get("auto_loading", None)) is not None:
                    self.auto_loading = value
                self.core.refresh(self)
            elif operation == "messagefeedback":
                message_id = data['message_id']
                del data['message_id']
                message = self.message_map[message_id]
                for key, value in data.items():
                    message['feedback'][key] = value
                self.send({
                    "operation": "updatemessage",
                    "message": message,
                })
        except Exception:  # pylint: disable=broad-except
            print(traceback.format_exc())
            self.send({
                "operation": "error",
                "command": operation,
                "message": traceback.format_exc(),
            })

    def receive_message(self, message: IChatMessage):
        """Receives message from user"""
        self.history.append(message)
        self.message_map[message['id']] = message
        self.send({
            "operation": "reply",
            "message": message
        })
        process_message = (
            message.get('kernelProcess') == KernelProcess.PROCESS
            and self.message_processing_enabled
            or message.get('kernelProcess') == KernelProcess.FORCE
        )
        if process_message:
            context = MessageContext(self, message)
            self.core.process_message(context)

    def receive_query(self, query_type, request_id, query):
        """Receives query from user"""
        if self.query_processing_enabled:
            self.core.process_query(self, query_type, request_id, query)
        else:
            self.send({
                "operation": "subjects",
                "responseId": request_id,
                "items": [],
            })

    def send(self, data):
        """Receives send results"""
        self.comm.send(data)

    def reply(self, text, type_="bot", reply=None):
        """Replies message to user"""
        message = MessageContext.create_message(text, type_, reply)
        self.reply_message(message)

    def reply_message(self, message: IChatMessage):
        """Replies IChatMessage to user"""
        self.history.append(message)
        self.message_map[message['id']] = message
        self.send({
            "operation": "reply",
            "message": message
        })
