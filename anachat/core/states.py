"""Chatbot state management"""

import re
import inspect
from functools import wraps
from lunr import lunr

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


def statemanager(func):
    """Wraps generator function to support waiting for user replies"""
    @wraps(func)
    def helper(*args, **kwargs):
        if inspect.isgeneratorfunction(func):
            gen = func(*args, **kwargs)
            try:
                next(gen)
            except StopIteration as exc:
                return exc.value
            else:
                return _GeneratorStateManager(gen)
        return func(*args, **kwargs)
    return helper


class _GeneratorStateManager:
    """State for wrapping generator. Pass user messages to yield positions"""

    def __init__(self, gen):
        self.gen = gen

    def process_message(self, comm, text):
        """Processes user messages"""
        try:
            self.gen.send(text)
        except StopIteration as exc:
            return exc.value
        return self


def build_document_list(tree):
    """Builds document list to use lunr for searching"""
    docmap = {}
    documents = []
    regexes = {}

    cid = 1
    visit = [("", tree)]
    while visit:
        current = visit.pop()
        newpath = current[0] + " " + current[1].name
        document = {
            'id': cid,
            'name': current[1].name,
            'path': newpath,
            'node': current[1],
        }
        if 'regex' in current[1].attr:
            regexes[current[1].attr['regex']] = document
        documents.append(document)
        docmap[str(cid)] = document
        cid += 1
        for child in current[1].children:
            child.parent = current[1]
            visit.append((newpath, child))
    return docmap, documents, regexes



class SubjectState:
    """State that uses document list for searching a subject"""

    def __init__(self, tree):
        self.docmap, documents, self.regexes = build_document_list(tree)
        self.idx = lunr(ref='id', fields=('name', 'path'), documents=documents)

    def process_message(self, comm, text):
        """Processes user messages"""
        if text.startswith("http://") or text.startswith("https://"):
            comm.open_panel(text, "URL View")
            return self
        for regex, document in self.regexes.items():
            result = re.search(regex, text)
            if result:
                return choose_state(comm, document['node'], self, self, matches=result)
        matches = self.idx.search(text)
        if not matches:
            comm.reply("I could not find this subject. Please, try a different query")
            return self
        return prepare_sub_choice_state(matches, comm, self)


def prepare_sub_choice_state(matches, comm, subjectstate):
    """Present subjects as choices"""
    label = f"I found {len(matches)} subjects. Which one of these best describe your query?"
    if len(matches) <= 6:
        return SubjectChoiceStateDefinition(matches, label, comm, subjectstate).materialize()

    states = []
    last = None
    for i, match_index in enumerate(range(0, len(matches), 6)):
        nextp = False
        submatches = matches[match_index: match_index + 6]
        if match_index + 6 < len(matches):
            nextp = True
        interval = f"{match_index + 1}..{min(match_index + 6, len(matches))}"
        state = SubjectChoiceStateDefinition(
            submatches,
            label + f" Showing {interval} (page {i + 1}).",
            comm, subjectstate, prevpage=last, nextpage=nextp
        )
        if last:
            last.nextpage = state
        last = state
        states.append(last)

    return states[0].materialize()


def choose_state(comm, node, subjectstate, previousstate, matches=None):
    """Navigate to state"""
    if "action" not in node.attr:
        return SubjectInfoState(comm, node, subjectstate, previousstate)
    return node.attr["action"](comm, subjectstate, previousstate, matches=matches)


class SubjectChoiceStateDefinition:
    """Represents a subject state"""
    def __init__(self, matches, label, comm, subjectstate, prevpage=None, nextpage=None):
        self.subjectstate = subjectstate
        self.label = label
        self.prevpage = prevpage
        self.nextpage = nextpage
        self.comm = comm
        options = []
        for i, match in enumerate(matches):
            label = subjectstate.docmap[match['ref']]['name']
            options.append((str(i + 1), label, self.load_subject_info(match)))
        if prevpage:
            options.append(('<', '(Go to previous page)', self.load_prevpage))
        if nextpage:
            options.append(('>', '(Go to next page)', self.load_nextpage))
        options.append(('0', '(Go back to subject search)', self.load_subjectstate))
        self.options = options

    def load_prevpage(self, comm):
        """Go to previous page"""
        return self.prevpage.materialize()

    def load_nextpage(self, comm):
        """Go to next page"""
        return self.nextpage.materialize()

    def load_subject_info(self, match):
        """Go to subject info"""
        def load_info(comm):
            return choose_state(
                comm,
                self.subjectstate.docmap[match['ref']]['node'],
                self.subjectstate, self
            )
        return load_info

    def load_subjectstate(self, comm):
        """Go to subject state"""
        return self.subjectstate

    def materialize(self):
        """Go to different page"""
        return SubjectChoiceState(self.label, self.comm, self.options)


class SubjectChoiceState(OptionsState):
    """Subject state"""

    def __init__(self, label, comm, options):
        self.label = label
        super().__init__(comm, options)


class SubjectInfoState(OptionsState):
    """Subject info state"""
    def __init__(self, comm, node, subjectstate, previousstate):
        self.label = f"What do you want to know about {node.name}?"
        self.node = node
        self.subjectstate = subjectstate
        self.previousstate = previousstate
        options = []
        cid = 1
        self.order = {}
        if "action" in self.node.attr:
            options.append((str(cid), "Perform it", self.attr("action")))
            cid += 1
        for key in self.node.attr:
            if key not in ("action", "regex"):
                options.append((str(cid), key.replace("_", " ").capitalize(), self.attr(key)))
                cid += 1
        if self.node.parent is not None:
            options.append(
                (str(cid), f"{self.node.parent.name} (parent)", self.subject(self.node.parent))
            )
            cid += 1
        for child in self.node.children:
            options.append((str(cid), f"{child.name} (child)", self.subject(child)))
            cid += 1
        options.append((str(cid), '(Back)', self.back))
        options.append(("0", '(Go back to subject search)', self.backsubject))
        super().__init__(comm, options)

    def attr(self, attr):
        """Go to attr state of subject info"""
        def attr_display(comm):
            value = self.node.attr[attr]
            if callable(value):
                return value(comm, self, self.subjectstate)
            else:
                comm.reply(value)
                self.initial(comm)
                return self
        return attr_display

    def subject(self, child):
        """Go to child subject"""
        def child_display(comm):
            return SubjectInfoState(comm, child, self.subjectstate, self)
        return child_display

    def back(self, comm):
        """Go to previous state"""
        self.previousstate.initial(comm)
        return self.previousstate

    def backsubject(self, comm):
        """Go to subject state"""
        return self.subjectstate


class DummyState:
    """Dummy state that only repeats user messages"""

    def process_message(self, comm, text):
        """Processes user messages"""
        comm.reply(text + ", ditto")
        return self


class SubjectTree:
    """Represents a subject"""

    def __init__(self, name, *children, **attr):
        self.name = name
        self.children = list(children)
        self.attr = attr
        self.parent = None

    def display(self, space_num=0):
        """Display subject as a tree"""
        padding = ' ' * space_num
        header = f"{padding}{self.name}"
        children = "\n".join(child.display(space_num + 2) for child in self.children)
        if children:
            children = f"(\n{children}\n{padding})"
        return f"{header}{children}"

    def __repr__(self):
        return self.display()
