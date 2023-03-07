"""Core Module that handles Ana operations"""
from __future__ import annotations
from typing import TYPE_CHECKING

import traceback


from .handlers.regex import RegexHandler
from .handlers.subject import SubjectHandler
from .handlers.url import URLHandler
from .resources import import_state_module
from .states.utils import GoToState, state_checkpoint


if TYPE_CHECKING:
    from typing import Iterable, Any
    from ..comm.anacomm import AnaComm
    from ..comm.message import MessageContext
    from .states.state import StateDefinition



class DefaultState:
    """Default Ana state"""

    def __init__(self):
        self.subject_handler = SubjectHandler()

        self.solvers = [
            RegexHandler(),
            URLHandler(),
            self.subject_handler,
        ]

    def process_message(self, context: MessageContext) -> StateDefinition:
        """Processes user message"""
        for solver in self.solvers:
            result = solver.process_message(context)
            if result:
                return result
        context.reply("I could not process this query. Please, try a different query",
                      checkpoint=state_checkpoint(self))
        return self

    def process_query(self, comm: AnaComm, instance: str, request_id: int, query: str):
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
            "instance": instance,
            "operation": "subjects",
            "responseId": request_id,
            "items": result,
        })


class AnaCore:
    """Implements ana chat"""

    def __init__(self):
        self.default_state = DefaultState()
        self.state = self.default_state

    def refresh(self, comm: AnaComm, instance: str):
        """Refresh chatbot"""
        # pylint: disable=no-self-use
        comm.send(comm.history_message("refresh", instance=instance))

    def set_state(
        self,
        context: MessageContext,
        new_state: StateDefinition,
        *,
        params: Iterable[Any] | None=None
    ):
        """Sets new state"""
        params = params or []
        process_now = False
        if new_state is True:
            self.state = self.default_state
        elif new_state is False:
            self.state = self.default_state
            process_now = True
        elif isinstance(new_state, str):
            if new_state.startswith('>'):
                process_now = True
                new_state = new_state[1:]
            if new_state.startswith("!subject"):
                self.set_state(context, self.default_state)
                self.state = self.default_state
                subject = new_state[9:]
                if subject:
                    subject_state = self.default_state.subject_handler.state_by_key(subject)
                    if not subject_state:
                        context.reply(f"Subject {subject} not found. Loading default state",
                                      checkpoint=state_checkpoint(self.default_state))
                        self.state = self.default_state
                    else:
                        self.set_state(context, subject_state(context))
            else:
                module_name, state_func = new_state.split("?", 1)
                module = import_state_module(module_name)
                if module is None:
                    context.reply(f"Module {module_name} not found! Back to default state",
                                  checkpoint=state_checkpoint(self.default_state))
                    self.state = self.default_state
                    return
                if not hasattr(module, state_func):
                    context.reply(f"State function {state_func} not found in {module_name}! "
                                  f"Back to default state",
                                  checkpoint=state_checkpoint(self.default_state))
                    self.state = self.default_state
                    return
                self.set_state(context, getattr(module, state_func)(context, *params))
        elif callable(new_state):
            self.set_state(context, new_state(context, *params))
        elif new_state:
            self.state = new_state
        else:
            self.state = self.default_state
        if process_now:
            self.process_message(context, control=False)

    def process_message(self, context: MessageContext, control:bool=True) -> None:
        """Processes user message"""
        if control:
            text = context.text
            if text == "!debug":
                context.reply(f"Current state: {self.state!r}",
                              checkpoint=state_checkpoint(self.state))
                return
            if text.startswith("!subject"):
                self.set_state(context, text)
                return
            if text.startswith("!show"):
                keys = text.split()[1:] or context.comm.memory.keys()
                result = []
                for key in keys:
                    result.append(f"{key}: {context.comm.memory.get(key, '!not found')}")
                context.reply("\n".join(result),
                              checkpoint=state_checkpoint(self.state))
                return

            reply = context.original_message.get('reply', '')
            history = context.comm.history
            if check_state := context.comm.checkpoints.get(reply, None):
                self.set_state(context, check_state)
                return
            elif reply and len(history) >= 2 and reply != history[-2]['id']:
                self.set_state(context, self.default_state)

        try:
            self.set_state(context, self.state.process_message(context))
        except GoToState as goto:
            self.set_state(context, goto.state, params=goto.params)
        except Exception:  # pylint: disable=broad-except
            self.set_state(context, self.default_state)
            context.reply("Something is wrong: " + traceback.format_exc(), "error",
                          checkpoint=state_checkpoint(self.state))

    def process_query(self, comm: AnaComm, instance: str, query_type: str, request_id: int, query: str):
        """Processes user query"""
        if query_type == "subject":
            self.default_state.process_query(comm, instance, request_id, query)


class DummyState:
    """Dummy state that only repeats user messages"""

    def process_message(self, context: MessageContext) -> StateDefinition:
        """Processes user messages"""
        # pylint: disable=unused-argument
        context.reply(context.text + ", ditto")
        return self

    def process_query(self, comm: AnaComm, instance: str, query_type: str, request_id: int, query: str):
        """Processes user query"""
        # pylint: disable=unused-argument
        # pylint: disable=no-self-use
        comm.send({
            "instance": instance,
            "operation": "subjects",
            "responseId": request_id,
            "items": [],
        })
