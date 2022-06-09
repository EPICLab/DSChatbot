"""State utility functions"""
import inspect
from functools import wraps

def statemanager(default=True):
    """Wraps generator function to support waiting for user replies"""
    def inner(func):
        """Inner decorator"""
        @wraps(func)
        def helper(*args, **kwargs):
            if inspect.isgeneratorfunction(func):
                gen = func(*args, **kwargs)
                try:
                    next(gen)
                except StopIteration as exc:
                    return exc.value or default
                else:
                    return _GeneratorStateManager(gen)
            return func(*args, **kwargs) or default
        return helper
    return inner


class _GeneratorStateManager:
    """State for wrapping generator. Pass user messages to yield positions"""

    def __init__(self, gen):
        self.gen = gen

    def process_message(self, comm, text):  # pylint: disable=unused-argument
        """Processes user messages"""
        try:
            self.gen.send(text)
        except StopIteration as exc:
            return exc.value
        return self


class GoToState(Exception):
    """Exception that supports the redirection of states"""

    def __init__(self, state, params=None):
        self.state = state
        self.params = params or []
        super().__init__(
            f"This exception should be handled by AnaCore to go to {state}"
        )

def create_reply_state(text):
    """Create a state that when enacted replies a text"""
    @statemanager()
    def reply_state(comm):
        """Replies predefined text and returns to default state"""
        comm.reply(text)
    return reply_state


def create_panel_state(url, title):
    """Create a state that when enacted opens a panel"""
    @statemanager()
    def panel_state(comm):
        """Opens a predefined panel and returns to default state"""
        comm.open_panel(url, title)
    return panel_state


def create_state_loader(state):
    """Create a state that loads a state by name when enacted"""
    @statemanager()
    def state_loader(comm):
        raise GoToState(state)
    return state_loader
