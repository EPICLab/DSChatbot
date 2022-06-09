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

        self.history = [{
            "text": "Hello, my name is Ana. How can I help you?",
            "type": "bot",
            "timestamp": datetime.timestamp(datetime.now()),
        }]
        self.options_actions = OptionsActions([], {})

    @property
    def core(self):
        """Returns current AnaCore"""
        return self.core_loader.core.CURRENT

    def register(self):
        """Registers comm"""
        self.comm = Comm(self.name)
        self.comm.on_msg(self.receive)
        self.send({
            "operation": "init",
            "history": self.history,
        })

    def receive(self, msg):
        """Receives requests"""
        data = msg["content"]["data"]
        operation = data.get("operation", "<undefined>")
        try:
            if operation == "message":
                self.receive_message(data.get("message"))
            elif operation == "refresh":
                self.core.refresh(self)
        except Exception:
            print(traceback.format_exc())
            self.send({
                "operation": "error",
                "command": operation,
                "message": traceback.format_exc(),
            })

    def receive_message(self, message):
        """Receives message from user"""
        self.history.append(message)
        self.core.process_message(self, message.get("text"))

    def send(self, data):
        """Receives send results"""
        self.comm.send(data)

    def reply(self, text, type_="bot"):
        """Replies message to user"""
        message = {
            "text": text,
            "type": type_,
            "timestamp": datetime.timestamp(datetime.now()),
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
