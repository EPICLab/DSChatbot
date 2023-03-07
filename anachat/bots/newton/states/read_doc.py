"""Defines interactions for loading dataset files"""
from __future__ import annotations
from typing import TYPE_CHECKING
from IPython.utils.text import format_screen

from .utils import statemanager


if TYPE_CHECKING:
    from ....comm.message import MessageContext
    from .state import StateGenerator


@statemanager()
def read_doc_state(
    context: MessageContext,
    oname: str
) -> StateGenerator:
    """Load documentation"""
    shell = context.comm.shell
    oname = 'pd'
    info = shell._object_find(oname, None)
    if info:
        #ip.inspector.pinfo(info.obj, oname, format_screen, info, enable_html_pager=True)
        inspector_info = shell.inspector._get_info(info.obj, oname, format_screen, info, 0)
        if 'text/plain' in inspector_info:
            context.reply(f"####text-panel#:{oname} documentation#:{inspector_info['text/plain']}")
        elif 'text/html' in inspector_info:
            context.reply(f"####html-panel#:{oname} documentation#:{inspector_info['text/html']}")
        else:
            context.reply(f"Documentation of {oname} not found. Make sure the object is loaded")
    else:
        context.reply(f"Documentation of {oname} not found. Make sure the object is loaded")
