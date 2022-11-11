"""Classification helpers"""
from __future__ import annotations
from typing import TYPE_CHECKING

from ..handlers.action import ActionHandler
from .utils import create_state_loader


if TYPE_CHECKING:
    from ..states.state import StateDefinition
    from ...comm.message import MessageContext


def classification_steps_state(context: MessageContext, class_state=None) -> StateDefinition:
    """Shows classification steps"""
    if class_state:
        context.comm.memory["class_state"] = class_state
    context.comm.memory["sub_state"] = "Classification"
    context.reply("Sounds good. Here are the steps for a classification:")
    ActionHandler().show_options(context, [
        {'key': '1', 'label': 'Preprocessing',
         'state': create_state_loader('!subject Classification > Preprocessing')},
        {'key': '2', 'label': 'Algorithm Specification',
         'state': create_state_loader('!subject Classification > Algorithm Specification')},
        {'key': '3', 'label': 'Validation',
         'state': create_state_loader('!subject Classification > Validation')},
        {'key': '4', 'label': 'Feature Engineering',
         'state': create_state_loader('!subject Classification > Feature Engineering')},
    ])
    return None
