import traceback
import os

import sys
import re



from .states import SubjectState, SubjectTree
from .tree.load_data import LOAD_DATA_SUBTREE
from .tree.preprocessing import PREPROCESSING_SUBTREE

# https://docs.google.com/document/d/1cb7JOcny_orNGfd7X9y6yI5pMFnU_Dxc/edit?rtpof=true


def classification_steps_state(comm, subjectstate, previousstate, matches=None):
    if matches and matches.group(2):
        comm.memory["class_state"] = matches.group(2)
    comm.memory["sub_state"] = "Classification"
    comm.reply("Sounds good. Here are the steps for a classification:")
    comm.reply([
        {'key': '1', 'label': 'Preprocessing'},
        {'key': '2', 'label': 'Algorithm Specification'},
        {'key': '3', 'label': 'Validation'},
        {'key': '4', 'label': 'Feature Engineering'},    
    ], "options")
    return subjectstate


TREE = SubjectTree(
    "",
    LOAD_DATA_SUBTREE,
    SubjectTree(
        "Classification",
        PREPROCESSING_SUBTREE,
        SubjectTree("Algorithm Specification"),
        SubjectTree("Validation"),
        SubjectTree("Feature Engineering"),
        action=classification_steps_state,
        regex="do a classification ?(of column (.*))"
    ),
)


class AnaCore(object):
    """Implements ana chat"""

    def __init__(self):
        self.state = SubjectState(TREE)

    def refresh(self, comm):
        """Refresh chatbot"""
        comm.send({
            "operation": "refresh",
            "history": comm.history,
        })

    def process_message(self, comm, text):
        """Processes user message"""
        if text == "!debug":
            comm.reply(f"Current state: {self.state!r}")
            return
        if text == "!subject":
            self.state = SubjectState(TREE)
            return
        if text.startswith("!show"):
            keys = text.split()[1:] or comm.memory.keys()
            result = []
            for key in keys:
                result.append(f"{key}: {comm.memory.get(key, '!not found')}")
            comm.reply("\n".join(result))
            return
        try:
            self.state = self.state.process_message(comm, text)
        except Exception:
            self.state = SubjectState(TREE)
            comm.reply("Something is wrong: " + traceback.format_exc(), "error")
