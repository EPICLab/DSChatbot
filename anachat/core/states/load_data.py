"""Defines interactions for loading dataset files"""

import os
from typing import Generator

from ...comm.context import MessageContext
from .utils import statemanager
from .state import StateDefinition


@statemanager()
def load_file_state(
    context: MessageContext,
    filename: str | None=None
) -> Generator[None, str, StateDefinition]:
    """Load file data"""
    def prepare_file(text):
        if os.path.exists(text):
            context.reply("Copy the following code to a cell:")
            code = ""
            ipython = context.comm.shell
            if 'pd' not in ipython.user_ns and 'pandas' not in ipython.user_ns:
                code = "import pandas as pd"
                pandas = "pd"
            elif 'pd' in ipython.user_ns:
                pandas = "pd"
            else:
                pandas = "pandas"
            code += f"\ndf = {pandas}.read_csv({text!r})\ndf"
            context.reply(code, type_="cell")
            return True
        context.reply("File does not exist. Try again or type !subject")
        return False

    if filename:
        result = prepare_file(filename)
        if result:
            return result
    context.reply("Please, write the name of the file")
    while True:
        text = yield
        result = prepare_file(text)
        if result:
            return result
