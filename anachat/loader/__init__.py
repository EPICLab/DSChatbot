"""Loader selector"""

try:
    from .newton_reloader import NewtonReloader as loader_cls
except ImportError:
    from .newton_loader import NewtonLoader as loader_cls
from .class_loader import class_loader

from ..bots.dummy import DummyBot
from ..bots.gpt import GPTBot

LOADERS =  {
    "newton": loader_cls,
    "dummy": class_loader(DummyBot),
    "gpt": class_loader(GPTBot),
}
