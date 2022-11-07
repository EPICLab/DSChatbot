"""Classification helpers"""
from ..handlers.action import ActionHandler
from .utils import create_state_loader


def classification_steps_state(comm, reply_to, class_state=None):
    """Shows classification steps"""
    if class_state:
        comm.memory["class_state"] = class_state
    comm.memory["sub_state"] = "Classification"
    comm.reply("Sounds good. Here are the steps for a classification:", reply=reply_to)
    ActionHandler().show_options(comm, [
        {'key': '1', 'label': 'Preprocessing',
         'state': create_state_loader('!subject Classification > Preprocessing')},
        {'key': '2', 'label': 'Algorithm Specification',
         'state': create_state_loader('!subject Classification > Algorithm Specification')},
        {'key': '3', 'label': 'Validation',
         'state': create_state_loader('!subject Classification > Validation')},
        {'key': '4', 'label': 'Feature Engineering',
         'state': create_state_loader('!subject Classification > Feature Engineering')},
    ], reply_to)
