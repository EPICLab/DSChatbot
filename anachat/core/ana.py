import traceback

from .states import OptionsState, SubjectState


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


class TypeConversionDecisionState(OptionsState):

    def __init__(self, comm, previousstate, subjectstate):
        self.label = f"What are the types?"
        self.subjectstate = subjectstate
        self.previousstate = previousstate
        options = [
            ("1", "DataFrame", self.text("Convert to Numpy Arrays")),
            ("2", "SparseMatrix", self.text("Convert to PandasSparseSeries")),
            ("3", "Image", self.text("Use TensorFlow extract_image_patches")),
            ("4", "(Back)", self.back),
            ("0", '(Go back to subject search)', self.backsubject),
        ]
        super().__init__(comm, options)

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

class AnaCore(object):
    """Implements ana chat"""

    def __init__(self):
        self.state = SubjectState(TREE)

    def refresh(self, comm):
        comm.send({
            "operation": "refresh",
            "history": comm.history,
        })

    def process_message(self, comm, text):
        try:
            self.state = self.state.process_message(comm, text)
        except:
            self.state = SubjectState(TREE)
            comm.reply("Something is wrong: " + traceback.format_exc(), "error")