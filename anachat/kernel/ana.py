from .anacomm import AnaComm

class AnaKernel(AnaComm):
    """Implements ana chat"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    
    def process_message(self, text):
        self.reply(text + ", ditto")
