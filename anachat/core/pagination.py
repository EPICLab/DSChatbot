"""Provides funcions for creating pagination"""

from typing import List, Tuple

from ..comm.context import MessageContext
from .handlers.action import ActionHandler, StatefulOption
from .states.utils import statemanager
from .states.state import StateCallable

PAGE_ID = 0


def create_page(page: int, count: int, items: List[StatefulOption], last: bool) -> StateCallable:
    """Creates page state"""
    @statemanager()
    def more_state(context: MessageContext):
        start_pos = (page - 1)*count + 1
        end_pos = start_pos + count - 1
        if last:
            end_pos = start_pos + len(items)
        context.reply(f"Showing {start_pos}..{end_pos} (page {page})")
        ActionHandler().show_options(context, items)
    return more_state


def _pagination(options: List[StatefulOption], count: int=5, page: int=1) -> Tuple[List[StatefulOption], bool]:
    """Splits options into pages"""
    global PAGE_ID  # pylint: disable=global-statement
    if len(options) <= count + 1:
        return options, True
    current, extra = options[:count], options[count:]
    key = f"<page {PAGE_ID}>"
    PAGE_ID += 1
    current.append({
        'key': key, 'label': "More...",
        'state': create_page(
            page, count, *_pagination(extra, count, page=page + 1)
        )
    })
    return current, False


def pagination(context: MessageContext, items: List[StatefulOption], *, count: int=5):
    """Paginates options and shows first page for consistency"""
    items, last = _pagination(items, count=count)
    if not last:
        context.reply(f"Showing 1..{count} (page 1)")
    ActionHandler().show_options(context, items)
