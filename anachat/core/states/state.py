"""Define state types"""
from __future__ import annotations

from typing import Generator, Protocol, TypeAlias, Any, Union

from ...comm.context import MessageContext

StateDefinition: TypeAlias = Union[None, bool, str, 'StateCallable', 'StateProtocol']

class StateCallable(Protocol):
    def __call__(self, context: MessageContext, *args: Any, **kwargs: Any) -> StateDefinition: ...

class StateGenerator(Protocol):
    def __call__(self, context: MessageContext, *args: Any, **kwargs: Any) -> Generator[None, str, StateDefinition]: ...

class StateProtocol(Protocol):
    def process_message(self, context: MessageContext) -> StateDefinition: ...
