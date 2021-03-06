"""Define a Comm for Ana"""
import traceback
from collections import defaultdict, namedtuple
from datetime import datetime
from ipykernel.comm import Comm
from .core_loader import BaseLoader

OptionsActions = namedtuple("OptionsActions", ['last', 'all'])


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
        self.loading = False

        self.history = [{
            "text": "Hello, my name is Ana. How can I help you?",
            "type": "bot",
            "timestamp": int(datetime.timestamp(datetime.now())*1000),
        }]
        self.options_actions = OptionsActions([], {})

    @property
    def core(self):
        """Returns current AnaCore"""
        return self.core_loader.core.CURRENT

    def history_message(self, opetation):
        """Returns message with history and general config"""
        return {
            "operation": opetation,
            "history": self.history,
            "message_processing_enabled": self.message_processing_enabled,
            "query_processing_enabled": self.query_processing_enabled,
            "loading": self.loading,
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
                    self.loading = value
                self.core.refresh(self)
        except Exception:  # pylint: disable=broad-except
            print(traceback.format_exc())
            self.send({
                "operation": "error",
                "command": operation,
                "message": traceback.format_exc(),
            })

    def receive_message(self, message):
        """Receives message from user"""
        self.history.append(message)
        self.send({
            "operation": "reply",
            "message": message
        })

        if not message.get('prevent') and self.message_processing_enabled or message.get('force'):
            self.core.process_message(self, message.get("text"))

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

    def reply(self, text, type_="bot"):
        """Replies message to user"""
        message = {
            "text": text,
            "type": type_,
            "timestamp": int(datetime.timestamp(datetime.now())*1000),
        }
        self.history.append(message)
        self.send({
            "operation": "reply",
            "message": message
        })

    def open_panel(self, url, title="Docs"):
        """Opens panel"""
        self.send({
            "operation": "panel",
            "url": url,
            "title": title,
        })
