"""Classification helpers"""
from __future__ import annotations
from typing import TYPE_CHECKING

from ..action import show_options
from .utils import create_state_loader


if TYPE_CHECKING:
    from ..states.state import StateDefinition
    from ...comm.message import MessageContext


def classification_steps_state(context: MessageContext, class_state=None) -> StateDefinition:
    """Shows classification steps"""
    if class_state:
        context.instance.memory["class_state"] = class_state
    context.instance.memory["sub_state"] = "Classification"
    show_options(context, [
        {'key': '1', 'label': 'Preprocessing',
         'state': create_state_loader('!subject Classification > Preprocessing')},
        {'key': '2', 'label': 'Algorithm Specification',
         'state': create_state_loader('!subject Classification > Algorithm Specification')},
        {'key': '3', 'label': 'Validation',
         'state': create_state_loader('!subject Classification > Validation')},
        {'key': '4', 'label': 'Feature Engineering',
         'state': create_state_loader('!subject Classification > Feature Engineering')},
    ], text="Sounds good. Here are the steps for a classification:")
    return None
