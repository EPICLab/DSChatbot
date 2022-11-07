"""Core Module that handles Ana operations"""
import traceback

from anachat.core.handlers.woz import WozHandler


from .handlers.action import ActionHandler
from .handlers.regex import RegexHandler
from .handlers.subject import SubjectHandler
from .handlers.url import URLHandler
from .resources import import_state_module
from .states.utils import GoToState


class DefaultState:
    """Default Ana state"""

    def __init__(self):
        self.subject_handler = SubjectHandler()

        self.solvers = [
            WozHandler(),
            ActionHandler(),
            RegexHandler(),
            URLHandler(),
            self.subject_handler,
        ]

    def process_message(self, comm, text, reply_to, replying_to):
        """Processes user message"""
        for solver in self.solvers:
            result = solver.process_message(comm, text, reply_to, replying_to)
            if result:
                return result
        comm.reply("I could not process this query. Please, try a different query", reply=reply_to)
        return self

    def process_query(self, comm, request_id, query):
        """Processes subject queries"""
        result = []
        for match, node in self.subject_handler.search(query):
            result.append({
                'type': 'subject',
                'key': match['ref'],
                'value': node.get('description', ''),
                'url': node.get('url', ''),
            })
        result = result[:5]
        comm.send({
            "operation": "subjects",
            "responseId": request_id,
            "items": result,
        })


class AnaCore:
    """Implements ana chat"""

    def __init__(self):
        self.default_state = DefaultState()
        self.state = self.default_state

    def refresh(self, comm):
        """Refresh chatbot"""
        # pylint: disable=no-self-use
        comm.send(comm.history_message("refresh"))

    def set_state(self, comm, new_state, reply_to, *, params=None):
        """Sets new state"""
        params = params or []
        if new_state is True:
            self.state = self.default_state
        elif isinstance(new_state, str):
            if new_state.startswith("!subject"):
                self.set_state(comm, self.default_state, reply_to)
                self.state = self.default_state
                subject = new_state[9:]
                if subject:
                    subject_state = self.default_state.subject_handler.state_by_key(subject, reply_to)
                    if not subject_state:
                        comm.reply(
                            f"Subject {subject} not found. Loading default state", reply=reply_to
                        )
                    else:
                        self.set_state(comm, subject_state(comm, reply_to), reply_to)
            else:
                module_name, state_func = new_state.split("?", 2)
                module = import_state_module(module_name)
                if module is None:
                    comm.reply(
                        f"Module {module_name} not found! Back to default state", reply=reply_to
                    )
                    self.state = self.default_state
                    return
                if not hasattr(module, state_func):
                    comm.reply(f"State function {state_func} not found in {module_name}! "
                               f"Back to default state", reply=reply_to)
                    self.state = self.default_state
                    return
                self.set_state(comm, getattr(module, state_func)(comm, reply_to, *params), reply_to)
        elif callable(new_state):
            self.set_state(comm, new_state(comm, reply_to, *params), reply_to)
        elif new_state:
            self.state = new_state
        else:
            self.state = self.default_state

    def process_message(self, comm, text, reply_to, replying_to):
        """Processes user message"""
        if text == "!debug":
            comm.reply(f"Current state: {self.state!r}", reply=reply_to)
            return
        if text.startswith("!subject"):
            self.set_state(comm, text, reply_to)
            return
        if text.startswith("!show"):
            keys = text.split()[1:] or comm.memory.keys()
            result = []
            for key in keys:
                result.append(f"{key}: {comm.memory.get(key, '!not found')}")
            comm.reply("\n".join(result), reply=reply_to)
            return
        try:
            self.set_state(
                comm, self.state.process_message(comm, text, reply_to, replying_to), reply_to
            )
        except GoToState as goto:
            self.set_state(comm, goto.state, reply_to, params=goto.params)
        except Exception:  # pylint: disable=broad-except
            self.set_state(comm, self.default_state, reply_to)
            comm.reply("Something is wrong: " + traceback.format_exc(), "error", reply=reply_to)

    def process_query(self, comm, query_type, request_id, query):
        """Processes user query"""
        if query_type == "subject":
            self.default_state.process_query(comm, request_id, query)


class DummyState:
    """Dummy state that only repeats user messages"""

    def process_message(self, comm, text, reply_to, replying_to):
        """Processes user messages"""
        # pylint: disable=unused-argument
        comm.reply(text + ", ditto", reply=reply_to)
        return self

    def process_query(self, comm, query_type, request_id, query):
        """Processes user query"""
        # pylint: disable=unused-argument
        # pylint: disable=no-self-use
        comm.send({
            "operation": "subjects",
            "responseId": request_id,
            "items": [],
        })
