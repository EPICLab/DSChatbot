"""Loader selector"""

try:
    from .core_reloader import CoreReloader as loader_cls
except ImportError:
    from .core_loader import BaseLoader as loader_cls


LOADERS =  {
    "base": loader_cls
}
