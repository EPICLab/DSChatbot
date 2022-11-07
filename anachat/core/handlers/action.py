"""Provides classes related to handling options"""


class ActionHandler:
    """Provides function for loading states based on actions"""

    def reset(self, comm):
        """Resets state of last options"""
        # pylint: disable=no-self-use
        comm.options_actions.last.clear()

    def add(self, comm, options):
        """Adds options to all options"""
        # pylint: disable=no-self-use
        if not isinstance(options, list):
            options = [options]
        for option in options:
            if 'state' not in option:
                continue
            comm.options_actions.last.append(option)
            comm.options_actions.all[f"!choose {option['key']}"] = option

    def show_options(self, comm, options):
        """Shows options that redirect to states"""
        self.reset(comm)
        self.add(comm, options)
        new_options = [{
            'key': option['key'],
            'label': f"{num + 1}. {option['label']}"
        } for num, option in enumerate(options)]
        comm.reply(new_options, "options")

    def process_message(self, comm, text):
        """Processes users message"""
        last = comm.options_actions.last[:]
        self.reset(comm)
        if text and text[0].isdigit() and ('.' in text or text.isdigit()):
            pos = int(text.split('.')[0])
            if pos <= len(last):
                return last[pos - 1]['state'](comm)

        for option in last:
            if option['key'] == text or option['label'].lower() == text.lower():
                return option['state'](comm)

        option = comm.options_actions.all.get(text, None)
        if option is not None:
            return option['state'](comm)
        return None


class OptionsState:
    """Presents a set of options and asks users to select one"""

    label = "Please, choose an option:"
    invalid = "I could not understand this option. Please, try again."

    def __init__(self, comm, options=None):
        self.options = options or []
        self.matches = {}
        for key, label, function in self.options:
            pkey, plabel = self.preprocess(key), self.preprocess(label)
            self.matches[pkey] = function
            self.matches[plabel] = function
            self.matches[f"{pkey}. {plabel}"] = function
        self.initial(comm)

    def initial(self, comm):
        """Presents label and options"""
        comm.reply(self.label)
        comm.reply([
            {'key': item[0], 'label': item[1]} for item in self.options
        ], "options")

    def preprocess(self, text):
        """Removes spaces at the beginning and ending of text and transform it to lowercase"""
        return str(text).strip().lower()

    def process_message(self, comm, text):
        """Processes user messages"""
        newtext = self.preprocess(text)
        if newtext in self.matches:
            function = self.matches[newtext]
            return function(comm)
        comm.reply(self.invalid)
        return self
