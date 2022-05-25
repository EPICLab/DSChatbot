"""Defines interactions for loading dataset files"""

import os
from ..states import SubjectTree, statemanager

@statemanager
def load_file_state(comm, subjectstate, previousstate, matches=None):
    """Load file data"""
    def prepare_file(text):
        newtext = str(text).strip().lower()
        if newtext == "<back>":
            return previousstate
        if newtext == "<subject>":
            return subjectstate
        if os.path.exists(text):
            comm.reply("Copy the following code to a cell:")
            code = ""
            ipython = comm.shell
            if 'pd' not in ipython.user_ns and 'pandas' not in ipython.user_ns:
                code = "import pandas as pd"
                pandas = "pd"
            elif 'pd' in ipython.user_ns:
                pandas = "pd"
            else:
                pandas = "pandas"
            code += f"\ndf = {pandas}.read_csv({text!r})\ndf"
            comm.reply(code, type_="cell")
            return subjectstate
        return None

    if matches and matches.group(1):
        result = prepare_file(matches.group(1))
        if result:
            return result
    comm.reply("Please, write the name of the file, type <back> to go back to the previous state or <subject> to go back to the subject search:")
    while True:
        text = yield
        result = prepare_file(text)
        if result:
            return result

LOAD_DATA_SUBTREE = SubjectTree(
    "Load data",
    action=load_file_state,
    regex="load data ?(.*)"
)
