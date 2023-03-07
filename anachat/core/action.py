"""Provides classes related to handling options"""
from __future__ import annotations
from typing import TYPE_CHECKING

from anachat.core.states.utils import statemanager


if TYPE_CHECKING:
    from typing import List, Optional, Tuple
    from ..comm.message import MessageContext, IOptionItem
    from .states.state import StateCallable, StateDefinition

    class StatefulOption(IOptionItem, total=False):
        """Defines an Option for a list of options"""
        state: Optional[StateCallable]


def show_options(
    context: MessageContext,
    options: List[StatefulOption],
    ordered: bool = True,
    text: str | None = None
) -> None:
    """Shows options that redirect to states"""
    @statemanager(False)
    def select_option(context: MessageContext):
        """State for option selection"""
        no_state = lambda _: None

        text = context.text
        if text and text[0].isdigit() and ('.' in text or text.isdigit()):
            pos = int(text.split('.')[0])
            if pos <= len(options):
                state = options[pos - 1].get('state', None) or no_state
                return state(context)

        for option in options:
            if option['key'] == text or option['label'].lower() == text.lower():
                state = option.get('state', None) or no_state
                return state(context)
    context.reply_options(options, ordered=ordered, checkpoint=select_option, text=text)
