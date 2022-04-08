import re
from lunr import lunr

class OptionsState:

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
        comm.reply(self.label)
        comm.reply([
            {'key': item[0], 'label': item[1]} for item in self.options
        ], "options")

    def preprocess(self, text):
        return str(text).strip().lower()

    def process_message(self, comm, text):
        newtext = self.preprocess(text)
        if newtext in self.matches:
            function = self.matches[newtext]
            return function(comm)
        comm.reply(self.invalid)
        return self


def build_document_list(tree):
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

    def __init__(self, tree):
        self.docmap, documents, self.regexes = build_document_list(tree)
        self.idx = lunr(ref='id', fields=('name', 'path'), documents=documents)

    def process_message(self, comm, text):
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
    label = f"I found {len(matches)} subjects. Which one of these best describe your query?"
    if len(matches) <= 6:
        return SubjectChoiceStateDefinition(matches, label, comm, subjectstate).materialize()

    states = []
    last = None
    for i, p in enumerate(range(0, len(matches), 6)):
        nextp = False
        submatches = matches[p: p + 6]
        if p + 6 < len(matches):
            nextp = True
        state = SubjectChoiceStateDefinition(submatches, label + f" Showing {p + 1}..{min(p + 6, len(matches))} (page {i + 1}).", comm, subjectstate, prevpage=last, nextpage=nextp)
        if last:
            last.nextpage = state
        last = state
        states.append(last)

    return states[0].materialize()


def choose_state(comm, node, subjectstate, previousstate, matches=None):
    if "action" not in node.attr:
        return SubjectInfoState(comm, node, subjectstate, previousstate)
    return node.attr["action"](comm, subjectstate, previousstate, matches=matches)


class SubjectChoiceStateDefinition:
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
        return self.prevpage.materialize()

    def load_nextpage(self, comm):
        return self.nextpage.materialize()

    def load_subject_info(self, match):
        def load_info(comm):
            return choose_state(comm, subjectstate.docmap[match['ref']]['node'], self.subjectstate, self)
        return load_info

    def load_subjectstate(self, comm):
        return self.subjectstate

    def materialize(self):
        return SubjectChoiceState(self.label, self.comm, self.options)


class SubjectChoiceState(OptionsState):

    def __init__(self, label, comm, options):
        self.label = label
        super().__init__(comm, options)


class SubjectInfoState(OptionsState):
    def __init__(self, comm, node, subjectstate, previousstate):
        self.label = f"What do you want to know about {node.name}?"
        self.node = node
        self.subjectstate = subjectstate
        self.previousstate = previousstate
        options = []
        cid = 1
        self.order = {}
        for key in self.node.attr:
            if key not in ("action", "regex"):
                options.append((str(cid), key.replace("_", " ").capitalize(), self.attr(key)))
                cid += 1
        if self.node.parent is not None:
            options.append((str(cid), f"{self.node.parent.name} (parent)", self.subject(self.node.parent)))
            cid += 1
        for child in self.node.children:
            options.append((str(cid), f"{child.name} (child)", self.subject(child)))
            cid += 1
        options.append((str(cid), '(Back)', self.back))
        options.append(("0", '(Go back to subject search)', self.backsubject))
        super().__init__(comm, options)

    def attr(self, attr):
        def attr_display(comm):
            value = self.node.attr[attr]
            if isinstance(value, type):
                return value(comm, self, self.subjectstate)
            else:
                comm.reply(value)
                self.initial(comm)
                return self
        return attr_display

    def subject(self, child):
        def child_display(comm):
            return SubjectInfoState(comm, child, self.subjectstate, self)
        return child_display

    def back(self, comm):
        self.previousstate.initial(comm)
        return self.previousstate

    def backsubject(self, comm):
        return self.subjectstate


class DummyState:

    def process_message(self, comm, text):
        comm.reply(text + ", ditto")        
        return self
    
