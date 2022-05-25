from ..states import OptionsState

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


"""
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
    """
