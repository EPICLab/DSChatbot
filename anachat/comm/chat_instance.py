"""Define a chat instance"""
from __future__ import annotations
from collections import defaultdict
import traceback
import weakref
from typing import TYPE_CHECKING
from ..loader import LOADERS
from .message import KernelProcess, MessageContext

if TYPE_CHECKING:
    from .kernelcomm import KernelComm
    from .message import IChatMessage


def apply_partial(original: dict, update: dict):
    """Apply nested changes to original dict"""
    for key, value in update.items():
        if isinstance(value, dict):
            apply_partial(original[key], value)
        else:
            original[key] = value


class ChatInstance:
    """Chat Instance handler"""

    def __init__(self, comm: KernelComm, chat_name: str, loader="base"):
        self.comm_ref = weakref.ref(comm)
        self.core_loader = LOADERS[loader](comm)
        self.memory = defaultdict(lambda: None)

        self.chat_name = chat_name

        self.history = []
        self.message_map = {}
        self.config = {
            "process_in_kernel": True,
            "enable_autocomplete": True,
            "enable_auto_loading": False,
            "loading": False,

            "show_replied": False,
            "show_index": False,
            "show_time": True,
            "show_build_messages": True,
            "show_kernel_messages": True,
        }

        self.history.append(MessageContext.create_message(
            ("Hello, I am Newton, an assistant that can help you with machine learning. "
             "You can ask me questions at any given time and go back to previous questions too. "
             "How can I help you?"),
            "bot"
        ))

        for message in self.history:
            self.message_map[message['id']] = message

        self.checkpoints = {}

    @property
    def core(self):
        """Returns current AnaCore"""
        return self.core_loader.current()

    def sync_chat(self, operation):
        """Sends message with history and general config"""
        self.send({
            "operation": operation,
            "history": self.history,
            "config": self.config,
        })

    def receive(self, data: dict):
        """Processes received requests"""
        try:
            operation = data["operation"]
            if operation == "message":
                self.receive_message(data.get("message"))
            elif operation == "refresh":
                self.core.refresh(self)
            elif operation == "autocomplete-query":
                self.receive_autocomplete_query(
                    data.get('requestId'),
                    data.get('query')
                )
            elif operation == "config":
                key = data["key"]
                value = data["value"]
                if data["_mode"] == "update" or key not in self.config:
                    self.config[key] = value
                self.send({
                    "operation": "update-config",
                    "config": {key: self.config[key]},
                })
            elif operation == "sync-message":
                partial_message = data["message"]
                message = self.message_map[partial_message["id"]]
                apply_partial(message, partial_message)
                self.send({
                    "operation": "update-message",
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
            and self.config["process_in_kernel"]
            or message.get('kernelProcess') == KernelProcess.FORCE
        )
        if process_message:
            context = MessageContext(self.comm_ref(), self, message)
            self.core.process_message(context)

    def receive_autocomplete_query(self, request_id, query):
        """Receives query from user"""
        if self.config["enable_autocomplete"]:
            self.core.process_autocomplete(self, request_id, query)
        else:
            self.send({
                "operation": "autocomplete-response",
                "responseId": request_id,
                "items": [],
            })

    def send(self, data):
        """Receives send results"""
        data["instance"] = self.chat_name
        self.comm_ref().comm.send(data)

    def reply_message(self, message: IChatMessage):
        """Replies IChatMessage to user"""
        self.history.append(message)
        self.message_map[message['id']] = message
        self.send({
            "operation": "reply",
            "message": message
        })
