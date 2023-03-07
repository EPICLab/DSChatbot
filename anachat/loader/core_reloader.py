
"""Defines loader that reloads core"""

from __future__ import annotations
from typing import TYPE_CHECKING
from types import ModuleType

import hashlib
import importlib
import os
import traceback

import pyinotify

from .core_loader import BaseLoader

if TYPE_CHECKING:
    from ..comm.kernelcomm import KernelComm

class CoreReloader(BaseLoader):
    """Loads the core chatbot module and reload it if necessary"""

    def __init__(self, comm: KernelComm):
        super().__init__(comm)
        self.basedir = os.path.dirname(self.core.__file__)
        self.modulehashes = {}
        for root, dirs, files in os.walk(self.basedir):
            for filename in files:
                if filename.endswith('.py'):
                    self.set_module_hash(os.path.join(root, filename))

        mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE | pyinotify.IN_MODIFY
        manager = pyinotify.WatchManager()
        notifier = pyinotify.ThreadedNotifier(
            manager, default_proc_fun=Reloader(reloader=self, comm=comm)
        )
        manager.add_watch(self.basedir, mask)
        notifier.start()

    def get_file_hash(self, fname):
        """Obtains hash from file"""
        hash_md5 = hashlib.md5()
        with open(fname, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def set_module_hash(self, fname):
        """Stores current file hash"""
        self.modulehashes[fname] = self.get_file_hash(fname)

    def check_recursive_change(self, module=None, comm=None):
        """Check for changes in folder recursively"""
        module = module or self.core
        result = []
        if hasattr(module, "__file__") and module.__file__.startswith(self.basedir):
            mpath = module.__file__
            for attribute_name in dir(module):
                attribute = getattr(module, attribute_name)
                if type(attribute) is ModuleType:  # pylint: disable=unidiomatic-typecheck
                    result.extend(self.check_recursive_change(attribute, comm=comm))
            if result or (self.get_file_hash(mpath) != self.modulehashes.get(mpath)):
                result.append(module)
        return result

    def reload_list(self, modules):
        """Recursively reloads modules."""
        for module in modules:
            importlib.reload(module)
            self.set_module_hash(module.__file__)


class Reloader(pyinotify.ProcessEvent):
    """Reloader for ipynotify"""

    def my_init(self, reloader=None, comm=None, **kwargs):
        """Initializes variables to use on process notification"""
        self._reloader = reloader
        self._comm = comm

    def process_default(self, event):
        # pylint: disable=unused-argument
        # pylint: disable=import-outside-toplevel
        # pylint: disable=broad-except
        try:
            toreload = self._reloader.check_recursive_change(comm=self._comm)
            if toreload:
                self._comm.reply("Reloading Ana Core")
                self._reloader.reload_list(toreload)
                from .. import core
                self._reloader.core = core
        except Exception:
            self._comm.reply(f"Failed to reload Ana: {traceback.format_exc()}", type_="error")
