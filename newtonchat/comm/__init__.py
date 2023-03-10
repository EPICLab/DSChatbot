"""Kernel definition"""
from .kernelcomm import KernelComm

COMM = None

def init():
    """Init Notebook communication"""
    # pylint: disable=undefined-variable, global-statement
    global COMM
    if COMM is None:
        COMM = KernelComm(get_ipython(), "newton")
    COMM.register()
