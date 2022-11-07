"""Provides class related to handling urls"""

class URLHandler:
    """Handler that opens Panel if user types a URL"""
    # pylint: disable=too-few-public-methods

    def process_message(self, comm, text, reply_to, replying_to):
        """Processes user message"""
        # pylint: disable=no-self-use
        if text.startswith("http://") or text.startswith("https://"):
            comm.open_panel(text, "URL View")
            return True
        return None
