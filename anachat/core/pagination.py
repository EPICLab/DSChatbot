"""Provides funcions for creating pagination"""
from __future__ import annotations
from typing import TYPE_CHECKING

from .action import show_options
from .states.utils import statemanager


if TYPE_CHECKING:
    from typing import List, Tuple
    from ..comm.message import MessageContext
    from .action import StatefulOption
    from .states.state import StateCallable


def create_page(page: int, count: int, items: List[StatefulOption], last: bool) -> StateCallable:
    """Creates page state"""
    @statemanager()
    def more_state(context: MessageContext):
        start_pos = (page - 1)*count + 1
        end_pos = start_pos + count - 1
        if last:
            end_pos = start_pos + len(items)
        show_options(
            context, items, ordered=False,
            text=f"Showing {start_pos}..{end_pos} (page {page})"
        )
    return more_state


def _pagination(
    options: List[StatefulOption],
    count: int=5,
    page: int=1
) -> Tuple[List[StatefulOption], bool]:
    """Splits options into pages"""
    if len(options) <= count + 1:
        return options, True
    current, extra = options[:count], options[count:]
    next_page = page + 1
    current.append({
        'key': f"<page {next_page}>",
        'label': "More...",
        'state': create_page(
            next_page, count, *_pagination(extra, count, page=next_page)
        )
    })
    return current, False


def pagination(
    context: MessageContext,
    items: List[StatefulOption],
    *,
    count: int=5,
    create_order: bool=True,
    text: str | None = None
):
    """Paginates options and shows first page for consistency"""
    if create_order:
        items = [{
            'key': item['key'],
            'label': f'{num + 1}. {item["label"]}',
            'state': item['state']
        } for num, item in enumerate(items)]
    items, last = _pagination(items, count=count)
    if not last:
        text = text + "\n" if text else ""
        text += f"Showing 1..{count} (page 1)"
    show_options(context, items, ordered=False, text=text)
