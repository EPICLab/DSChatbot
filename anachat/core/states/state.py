"""Define state types"""
from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from typing import Generator, Protocol, TypeAlias, Any, Union, Optional

    from ...comm.message import MessageContext

    StateDefinition: TypeAlias = Union[None, bool, str, 'StateCallable', 'StateProtocol']
    StateGenerator: TypeAlias = Generator[None, str, StateDefinition]

    class StateCallable(Protocol):
        def __call__(
            self, context: MessageContext, *args: Any, **kwargs: Any
        ) -> StateDefinition: ...

    class StateGeneratorFunc(Protocol):
        def __call__(
            self, context: MessageContext, *args: Any, **kwargs: Any
        ) -> StateGenerator: ...

    class StateProtocol(Protocol):
        def process_message(self, context: MessageContext) -> StateDefinition: ...
