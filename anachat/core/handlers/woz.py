"""Provides class related to handling urls"""

class WozHandler:
    """Handler that does not do anything for wizard of woz"""
    # pylint: disable=too-few-public-methods

    def process_message(self, comm, text):
        """Processes user message"""
        # pylint: disable=no-self-use
        if text.startswith(">"):
            return True
        return None
