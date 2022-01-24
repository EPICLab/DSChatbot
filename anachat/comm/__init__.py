"""Anachat Kernel analysis"""
from .anacomm import AnaComm
try:
    from .core_reloader import CoreReloader as loader_cls
except ImportError:
    from .core_loader import BaseLoader as loader_cls

COMM = None

def init():
    """Init Ana"""
    # pylint: disable=undefined-variable, global-statement
    global COMM
    if COMM is None:
        COMM = AnaComm(get_ipython(), loader_cls)
    COMM.register()
