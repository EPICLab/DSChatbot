"""Provides class related to handling regexes"""
import json
import re


from ..resources import data
from ..states.utils import GoToState
from .utils import HandlerWithPaths


class RegexHandler(HandlerWithPaths):
    """Handler that loads state based on regex"""

    def __init__(self):
        self.regexes = []
        super().__init__()

    def load_file(self, filepath):
        """Load regex definition file"""
        with open(filepath, 'r', encoding='utf-8') as subjects:
            regexes = json.load(subjects)
        for regex in regexes:
            if 'redirect' in regex:
                self.load_file(data() / regex['redirect'])
            else:
                self.regexes.append(regex)
        self.paths[filepath] = self.getmtime(filepath)

    def inner_reload(self):
        """Reloads regexes definition"""
        self.regexes = []
        self.paths = {}
        self.load_file(data() / 'regexes.json')

    def inner_process_message(self, comm, text, reply_to, replying_to):
        """Processes user message"""
        for regex in self.regexes:
            matches = re.search(regex['regex'], text)
            if matches:
                param_defs = regex.get('params', [])
                params = []
                for param in param_defs:
                    try:
                        params.append(matches.group(param))
                    except IndexError:
                        params.append(None)
                raise GoToState(regex['state'], params)
        return None
