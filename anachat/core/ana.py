class AnaCore(object):
    """Implements ana chat"""

    def refresh(self, comm):
        comm.send({
            "operation": "refresh",
            "history": comm.history,
        })

    def process_message(self, comm, text):
        comm.reply(text + ", ditto")
