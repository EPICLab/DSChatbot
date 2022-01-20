class AnaCore(object):
    """Implements ana chat"""

    def refresh(self, comm):
        comm.send({
            "operation": "refresh",
            "history": comm.history,
        })

    def process_message(self, comm, text):
        comm.reply(text + ", ditto")


"""
Changing the core live inside jupyter:

>>> import anachat.core
>>> 
>>> class NewCore(anachat.core.AnaCore):
>>>     def process_message(self, comm, text):
>>>         comm.reply(text + ", ditto2")
>>> 
>>> anachat.core.CURRENT = NewCore()
"""