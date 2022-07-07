"""Defines interactions for print statements"""

import os
from .utils import statemanager


@statemanager()
def display_state(comm, text=None):
    """Display print statement"""
    if text is None:
        comm.reply("Please, write the display text")
        text = yield
    if text:
        checkchar = text[0]
        if checkchar in ('f', 'F') and len(text) > 1:
            checkchar = text[1]
            text = text[1:]
        if checkchar in ("'", '"'):
            string = text
        else:
            split = text.split(' ')
            for word in split:
                if word in comm.shell.user_ns:
                    iterpolated = ' '.join(('{' + wor + '}') if wor in comm.shell.user_ns else wor for wor in split)
                    comm.reply(f"""Your message is ambiguous. I am not sure if you want to include the value of the variable <b>{word}</b> in
your message or if you just want to print the text <span style="color: rgb(186, 33, 33);">'{text}'</span>. Quotation marks can
help to distinguish the text that you want to print from the elements of the code. Additionally, you
can use interpolation to add your variables in strings. Thus, if your intention is to include the value of
reply, you can use the string <span style="color: rgb(186, 33, 33);">f'{iterpolated}'</span>. Can you type again the message you
want to show in an unambiguous way?""")
                    return True
            string = "'" + text + "'"

    if '{' in string:  # ToDo use string.Formatter
        string = 'f' + string
    comm.reply("Copy the following code to a cell:")
    code = "print({})".format(string)
    comm.reply(code, type_="cell")
    return True
