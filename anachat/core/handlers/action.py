"""Provides classes related to handling options"""
from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from typing import List, Optional, Tuple
    from ...comm.anacomm import AnaComm
    from ...comm.message import MessageContext, IOptionItem
    from ..states.state import StateCallable, StateDefinition

    class StatefulOption(IOptionItem, total=False):
        """Defines an Option for a list of options"""
        state: Optional[StateCallable]


class ActionHandler:
    """Provides function for loading states based on actions"""

    def reset(self, comm: AnaComm) -> None:
        """Resets state of last options"""
        # pylint: disable=no-self-use
        comm.options_actions.last.clear()

    def add(self, comm: AnaComm, options: List[StatefulOption]) -> None:
        """Adds options to all options"""
        # pylint: disable=no-self-use
        if not isinstance(options, list):
            options = [options]
        for option in options:
            if 'state' not in option:
                continue
            comm.options_actions.last.append(option)
            comm.options_actions.all[f"!choose {option['key']}"] = option

    def show_options(self, context: MessageContext, options: List[StatefulOption]) -> None:
        """Shows options that redirect to states"""
        self.reset(context.comm)
        self.add(context.comm, options)
        new_options: List[IOptionItem] = [{
            'key': option['key'],
            'label': f"{num + 1}. {option['label']}"
        } for num, option in enumerate(options)]
        context.reply(new_options, "options")

    def process_message(self, context: MessageContext) -> StateDefinition:
        """Processes users message"""
        text = context.text
        last = context.comm.options_actions.last[:]
        self.reset(context.comm)
        if text and text[0].isdigit() and ('.' in text or text.isdigit()):
            pos = int(text.split('.')[0])
            if pos <= len(last):
                return last[pos - 1]['state'](context)

        for option in last:
            if option['key'] == text or option['label'].lower() == text.lower():
                return option['state'](context)

        option = context.comm.options_actions.all.get(text, None)
        if option is not None:
            return option['state'](context)
        return None


class OptionsState:
    """Presents a set of options and asks users to select one"""

    label = "Please, choose an option:"
    invalid = "I could not understand this option. Please, try again."

    def __init__(self, context: MessageContext, options: List[Tuple[str, str, StateCallable]] | None=None):
        self.options: List[Tuple[str, str, StateCallable]] = options or []
        self.matches = {}
        for key, label, function in self.options:
            pkey, plabel = self.preprocess(key), self.preprocess(label)
            self.matches[pkey] = function
            self.matches[plabel] = function
            self.matches[f"{pkey}. {plabel}"] = function
        self.initial(context)

    def initial(self, context: MessageContext) -> None:
        """Presents label and options"""
        context.reply(self.label)
        context.reply([
            {'key': item[0], 'label': item[1]} for item in self.options
        ], "options")

    def preprocess(self, text: str) -> str:
        """Removes spaces at the beginning and ending of text and transform it to lowercase"""
        return str(text).strip().lower()

    def process_message(self, context: MessageContext) -> StateDefinition:
        """Processes user messages"""
        # pylint: disable=unused-argument
        newtext = self.preprocess(context.text)
        if newtext in self.matches:
            function = self.matches[newtext]
            return function(context)
        context.reply(self.invalid)
        return self
