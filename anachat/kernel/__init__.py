"""Anachat Kernel analysis"""
from .ana import AnaKernel

COMM = None

def init():
    """Init Ana"""
    # pylint: disable=undefined-variable, global-statement
    global COMM
    COMM = AnaKernel(get_ipython())
    COMM.register()
