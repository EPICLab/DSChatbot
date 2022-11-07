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

    def show_options(self, comm, options, reply_to):
        """Shows options that redirect to states"""
        self.reset(comm)
        self.add(comm, options)
        new_options = [{
            'key': option['key'],
            'label': f"{num + 1}. {option['label']}"
        } for num, option in enumerate(options)]
        comm.reply(new_options, "options", reply=reply_to)

    def process_message(self, comm, text, reply_to, replying_to):
        """Processes users message"""
        last = comm.options_actions.last[:]
        self.reset(comm)
        if text and text[0].isdigit() and ('.' in text or text.isdigit()):
            pos = int(text.split('.')[0])
            if pos <= len(last):
                return last[pos - 1]['state'](comm, reply_to)

        for option in last:
            if option['key'] == text or option['label'].lower() == text.lower():
                return option['state'](comm, reply_to)

        option = comm.options_actions.all.get(text, None)
        if option is not None:
            return option['state'](comm, reply_to)
        return None


class OptionsState:
    """Presents a set of options and asks users to select one"""

    label = "Please, choose an option:"
    invalid = "I could not understand this option. Please, try again."

    def __init__(self, comm, reply_to, options=None):
        self.reply_to = reply_to
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
        comm.reply(self.label, reply=self.reply_to)
        comm.reply([
            {'key': item[0], 'label': item[1]} for item in self.options
        ], "options", reply=self.reply_to)

    def preprocess(self, text):
        """Removes spaces at the beginning and ending of text and transform it to lowercase"""
        return str(text).strip().lower()

    def process_message(self, comm, text, reply_to, replying_to):
        """Processes user messages"""
        # pylint: disable=unused-argument
        newtext = self.preprocess(text)
        if newtext in self.matches:
            function = self.matches[newtext]
            return function(comm, reply_to)
        comm.reply(self.invalid, reply=reply_to)
        return self
