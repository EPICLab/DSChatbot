"""Defines interactions for input statements"""

import os
from .utils import statemanager


@statemanager()
def ask_state(comm, text=None):
    """Display print statement"""
    if text is None:
        comm.reply("Please, write the input text")
        text = yield
    comm.reply(f"""If you just ask for input and do not store it, it will be lost for future interactions and usage. You could
store it in a <b>variable</b>? to be able to access it during the execution of your program. Do you want to
do it?""")
    code = f'input("{text}")'
    while True:
        yesno = yield
        if yesno.lower() in ('y', 'yes', 'sure', 'of course'):
            comm.reply("What name do you want to use for the variable? (Suggestion: reply)")
            variable = yield
            code = f"{variable} = {code}"
            break
        elif yesno.lower() in ('n', 'no', 'nope'):
            break
        elif yesno.lower() in ('exit', 'quit', 'return'):
            return True
        comm.reply('I could not understand the options. Please, answer "yes"/"no" or type "exit" to go back')

    comm.reply("Copy the following code to a cell:")
    comm.reply(code, type_="cell")
    return True
