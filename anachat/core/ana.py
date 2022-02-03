import math
import traceback
from lunr import lunr

class SubjectTree:

    def __init__(self, name, *children, **attr):
        self.name = name
        self.children = list(children)
        self.attr = attr
        self.parent = None
    
    def display(self, n=0):
        padding = ' ' * n
        header = f"{padding}{self.name}"
        children = f"\n".join(child.display(n + 2) for child in self.children)
        if children:
            children = f"(\n{children}\n{padding})"
        return f"{header}{children}"
        
    def __repr__(self):
        return self.display()

class TypeConversionDecisionState:

    def __init__(self, comm, previousstate, subjectstate):
        self.subjectstate = subjectstate
        self.previousstate = previousstate
        self.order = {
            "1": ("DataFrame", self.text("Convert to Numpy Arrays")),
            "2": ("SparseMatrix", self.text("Convert to PandasSparseSeries")),
            "3": ("Image", self.text("Use TensorFlow extract_image_patches")),
            "4": ("(Back)", self.back),
            "0": ('(Go back to subject search)', self.backsubject),
        }
        self.initial(comm)

    def text(self, text):
        def text_display(comm):
            comm.reply(text)
            self.initial(comm)
            return self
        return text_display

    def back(self, comm):
        self.previousstate.initial(comm)
        return self.previousstate

    def backsubject(self, comm):
        return self.subjectstate

    def initial(self, comm):
        text = f"What are the types?"
        order_text = "\n".join(
            f"{i}. {order_tup[0]}" for i, order_tup in self.order.items()
        )
        comm.reply(f"{text}\n{order_text}")
    
    def process_message(self, comm, text):
        strip = text.strip()
        if strip in self.order:
            return self.order[strip][1](comm)
        for order_tup in self.order.values():
            if strip.lower() == order_tup[0].lower():
                return order_tup[1](comm)
        comm.reply("I could not understand this option. Please, try again.")
        return self


TREE = SubjectTree(
    "",
    SubjectTree("Prediction"),
    SubjectTree(
        "Classifier",
        SubjectTree(
            "Data Manipulation/Wrangling",
            SubjectTree(
                "Building Data Set",
                SubjectTree("Type Mismatch")),
            SubjectTree(
                "Transformation", 
                SubjectTree("Type Conversion", help_to_choose_conversion=TypeConversionDecisionState),
                SubjectTree("Vectorizing", general_information="Vectorization is the process of converting an algorithm from operating on a single value at a time to operating on a set of value at one time"),
            ),
        ),
        SubjectTree(
            "Model",
            SubjectTree(
                "Regression",
                SubjectTree(
                    "Logistic Regression",
                    SubjectTree("Locally Weighted IR"),
                    SubjectTree(
                        "Softmax",
                        SubjectTree("F1"),
                        SubjectTree("Precision"),
                        SubjectTree(
                            "Accuracy",
                            SubjectTree(
                                "Optimizer",
                                SubjectTree("Adam"),
                                SubjectTree("AdaGrad"),
                                SubjectTree("RMSProp"),
                            ),
                        ),
                    ),
                ),
                SubjectTree(
                    "Linear Regression",
                    SubjectTree(
                        "Ordinary Least Squares",
                        SubjectTree("Best Fit Plot"),
                    ),
                    SubjectTree(
                        "Lasso (L1 Regularization)",
                        SubjectTree("Convergence")
                    ),
                ),
            ),
        ),
    ),
)


def build_document_list(tree):
    docmap = {}
    documents = []

    cid = 1
    visit = [("", tree)]
    while visit:
        current = visit.pop()
        newpath = current[0] + " " + current[1].name
        document = {
            'id': cid,
            'name': current[1].name,
            'path': newpath,
            'node': current[1]
        }
        documents.append(document)
        docmap[str(cid)] = document
        cid += 1
        for child in current[1].children:
            child.parent = current[1]
            visit.append((newpath, child))
    return docmap, documents




class AnaCore(object):
    """Implements ana chat"""

    def __init__(self):
        self.state = SubjectState()

    def refresh(self, comm):
        comm.send({
            "operation": "refresh",
            "history": comm.history,
        })

    def process_message(self, comm, text):
        try:
            self.state = self.state.process_message(comm, text)
        except:
            self.state = SubjectState()
            comm.reply("Something is wrong: " + traceback.format_exc(), "error")


class SubjectState:

    def __init__(self):
        self.docmap, documents = build_document_list(TREE)
        self.idx = lunr(ref='id', fields=('name', 'path'), documents=documents)

    def process_message(self, comm, text):
        matches = self.idx.search(text)
        if not matches:
            comm.reply("I could not find this subject. Please, try a different query")
            return self
        return SubjectChoiceState(matches, comm, self)


class SubjectChoiceState:

    def __init__(self, matches, comm, subjectstate):
        self.order = {str(i + 1): subjectstate.docmap[match['ref']] for i, match in enumerate(matches)}
        self.subjectstate = subjectstate
        self.initial(comm)
        
    def initial(self, comm):
        order_text = "\n".join(
            f"{i}. {match['name']}" for i, match in self.order.items()
        )
        order_text += "\n0. (Go back to subject search)"
        comm.reply(f"I found {len(self.order)} subjects. Which one of these best describe your query?\n{order_text}")

    def process_message(self, comm, text):
        strip = text.strip()
        if strip == "0":
            return self.subjectstate
        if strip in self.order:
            return SubjectInfoState(comm, self.order[strip]["node"], self.subjectstate, self)
        for match in self.order.values():
            if strip.lower() == match['name'].lower():
                return SubjectInfoState(comm, match["node"], self.subjectstate, self)
        comm.reply("I could not understand this option. Please, try again.")
        return self


class SubjectInfoState:
    def __init__(self, comm, node, subjectstate, previousstate):
        self.node = node
        self.subjectstate = subjectstate
        self.previousstate = previousstate
        cid = 1
        self.order = {}
        for key in self.node.attr:
            self.order[str(cid)] = (key.replace("_", " ").capitalize(), self.attr(key))
            cid += 1
        if self.node.parent is not None:
            self.order[str(cid)] = (f"{self.node.parent.name} (parent)", self.subject(self.node.parent))
            cid += 1
        for child in self.node.children:
            self.order[str(cid)] = (f"{child.name} (child)", self.subject(child))
            cid += 1

        self.order[str(cid)] = ('(Back)', self.back)
        self.order["0"] = ('(Go back to subject search)', self.backsubject)

        self.initial(comm)

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

    def initial(self, comm):
        text = f"What do you want to know about {self.node.name}?"
        order_text = "\n".join(
            f"{i}. {order_tup[0]}" for i, order_tup in self.order.items()
        )
        comm.reply(f"{text}\n{order_text}")
    
    def process_message(self, comm, text):
        strip = text.strip()
        if strip in self.order:
            return self.order[strip][1](comm)
        for order_tup in self.order.values():
            if strip.lower() == order_tup[0].lower():
                return order_tup[1](comm)
        comm.reply("I could not understand this option. Please, try again.")
        return self

class DummyState:

    def process_message(self, comm, text):
        comm.reply(text + ", ditto")        
        return self
    
