"""Provides funcions for creating pagination"""

from .handlers.action import ActionHandler
from .states.utils import statemanager

PAGE_ID = 0


def create_page(page, count, items, last):
    """Creates page state"""
    @statemanager()
    def more_state(comm, reply_to):
        start_pos = (page - 1)*count + 1
        end_pos = start_pos + count - 1
        if last:
            end_pos = start_pos + len(items)
        comm.reply(f"Showing {start_pos}..{end_pos} (page {page})", reply=reply_to)
        ActionHandler().show_options(comm, items, reply_to)
    return more_state


def _pagination(options, count=5, page=1):
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


def pagination(comm, items, reply_to, *, count=5):
    """Paginates options and shows first page for consistency"""
    items, last = _pagination(items, count=count)
    if not last:
        comm.reply(f"Showing 1..{count} (page 1)", reply=reply_to)
    ActionHandler().show_options(comm, items, reply_to)
