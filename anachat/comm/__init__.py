"""Anachat Kernel analysis"""
from .anacomm import AnaComm

COMM = None

def init():
    """Init Ana"""
    # pylint: disable=undefined-variable, global-statement
    global COMM
    if COMM is None:
        COMM = AnaComm(get_ipython())
    COMM.register()
