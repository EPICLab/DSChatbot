"""Define a Comm for Ana"""
import traceback
from datetime import datetime

from ipykernel.comm import Comm

class AnaComm(object):
    """Ana comm hadler"""
    # pylint: disable=useless-object-inheritance

    def __init__(self, shell=None):
        self.shell = shell
        self.name = "anachat.comm"
        self.comm = None

        self.history = []

    def register(self):
        """Register comm"""
        self.comm = Comm(self.name)
        self.comm.on_msg(self.receive)
        self.history = [{
            "text": "Hello, my name is Ana. How can I help you?",
            "type": "bot",
            "timestamp": datetime.timestamp(datetime.now()),
        }]
        self.send({
            "operation": "init",
            "history": self.history,
        })

    def receive(self, msg):
        """Receive requests"""
        data = msg["content"]["data"]
        operation = data.get("operation", "<undefined>")
        try:
            if operation == "message":
                self.receive_message(data.get("message"))
            elif operation == "refresh":
                self.refresh()
        except Exception:
            self.send({
                "operation": "error",
                "command": operation,
                "message": traceback.format_exc(),
            })

    def receive_message(self, message):
        self.history.append(message)
        self.process_message(message.get("text"))

    def send(self, data):
        """Receive send results"""
        self.comm.send(data)

    def reply(self, text, type_="bot"):
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

    def refresh(self):
        self.send({
            "operation": "refresh",
            "history": self.history,
        })
