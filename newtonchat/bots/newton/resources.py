"""Handle project resources"""
import importlib

MODULE = __name__
MODULE = MODULE[:MODULE.rfind(".")]
MODULE = MODULE[:MODULE.rfind(".")]
MODULE = MODULE[:MODULE.rfind(".")]

def project():
    """Returns project resources path"""
    return importlib.resources.files(MODULE)

def data():
    """Returns project data path"""
    return project() / 'data'

def import_state_module(module_name, reload=True):
    """Returns state module"""
    try:
        module = importlib.import_module(f'.bots.newton.states.{module_name}', MODULE)
        if reload:
            module = importlib.reload(module)
        return module
    except ModuleNotFoundError:
        return None
