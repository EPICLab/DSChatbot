"""Kernel definition"""
from .kernelcomm import KernelComm

COMM = None

def init():
    """Init Ana"""
    # pylint: disable=undefined-variable, global-statement
    global COMM
    if COMM is None:
        COMM = KernelComm(get_ipython(), "base")
    COMM.register()
