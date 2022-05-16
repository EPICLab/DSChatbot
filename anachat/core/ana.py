import traceback
import os
import inspect
import sys
import re



from .states import OptionsState, SubjectState

# https://docs.google.com/document/d/1cb7JOcny_orNGfd7X9y6yI5pMFnU_Dxc/edit?rtpof=true


from functools import wraps

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

    def __init__(self, gen):
        self.gen = gen

    def process_message(self, comm, text):
        try:
            self.gen.send(text)
        except StopIteration as exc:
            return exc.value
        return self

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


@statemanager
def load_file_state(comm, subjectstate, previousstate, matches=None):
    def prepare_file(text):
        newtext = str(text).strip().lower()
        if newtext == "<back>":
            return previousstate
        if newtext == "<subject>":
            return subjectstate
        if os.path.exists(text):
            comm.reply("Copy the following code to a cell:")
            code = ""
            ip = comm.shell
            if 'pd' not in ip.user_ns and 'pandas' not in ip.user_ns:
                code = "import pandas as pd"
                pandas = "pd"
            elif 'pd' in ip.user_ns:
                pandas = "pd"
            else:
                pandas = "pandas"
            code += f"\ndf = {pandas}.read_csv({text!r})\ndf"
            comm.reply(code, type_="cell")
            return subjectstate
        return None

    
    if matches and matches.group(1):
        result = prepare_file(matches.group(1))
        if result:
            return result
    comm.reply("Please, write the name of the file, type <back> to go back to the previous state or <subject> to go back to the subject search:")
    while True:
        text = yield
        result = prepare_file(text)
        if result:
            return result


def classification_steps_state(comm, subjectstate, previousstate, matches=None):
    if matches and matches.group(2):
        comm.memory["class_state"] = matches.group(2)
    comm.memory["sub_state"] = "Classification"
    comm.reply("Sounds good. Here are the steps for a classification:")
    comm.reply([
        {'key': '1', 'label': 'Preprocessing'},
        {'key': '2', 'label': 'Algorithm Specification'},
        {'key': '3', 'label': 'Validation'},
        {'key': '4', 'label': 'Feature Engineering'},
        
    ], "options")
    return subjectstate



@statemanager
def select_column_state(comm, subjectstate, previousstate, matches=None):
    if matches and matches.group(1):
        column = matches.group(1)
    else:
        comm.reply("Please, write the column name")
        column = yield
    comm.memory["column"] = column
    comm.reply(f'Selected column {column!r}')
    return subjectstate


def isdataframe(value):
    if 'pandas' in sys.modules:
        import pandas as pd
        return isinstance(value, pd.DataFrame)
    return str(type(value)) == "<class 'pandas.core.frame.DataFrame'>"


def get_dataframes(comm):
    for var, value in comm.shell.user_ns.items():
        if isdataframe(value):
            yield var

def select_dataframe(comm, matches):
    if matches and matches.group('df'):
        dataframe = matches.group('df')
    elif comm.memory['dataframe']:
        dataframe = comm.memory['dataframe']
    else:
        options = [
            {'key': i + 1, 'label': df} for i, df in enumerate(get_dataframes(comm))
        ]
        if not options:
            comm.reply("I could not find any dataframe in your notebook. Please write the expression of the dataframe")
        else:
            comm.reply("Please, select a dataframe")
            comm.reply(options, "options")
        dataframe = yield
    return dataframe

def select_column(comm, matches):
    if matches and matches.group('column'):
        column = matches.group('column')
        if column.startswith("column "):
            column = column[7:]
    elif comm.memory['column']:
        column = comm.memory['column']
    else:
        comm.reply("Please, write the column name")
        column = yield
    return column

@statemanager
def tokenize_column_state(comm, subjectstate, previousstate, matches=None):
    instructions = matches and matches.group(1) or ""

    dataframe = yield from select_dataframe(comm, re.search(r"from (dataframe )?(?P<df>.+?(?=( column )|$))", instructions))
    column = yield from select_column(comm, re.search(r"((^(?!from))|(column ))(?P<column>.+?(?=( from )|$))", instructions))
    

    comm.reply(f'For tokenizing {column!r} from {dataframe!r}, please copy the following code to a cell:')
    code = ""
    if 'nltk' not in comm.shell.user_ns:
        code = "import nltk\n"

    code += f"{dataframe}['tokenized_{column}'] = {dataframe}.apply(lambda row: nltk.word_tokenize(row[{column!r}]), axis=1)"
    comm.reply(code, type_="cell")
    return subjectstate

def apply_str_list_operation(comm, description, dataframe, column, prefix, str_op, list_op, code=""):
    if column in (df := comm.shell.user_ns.get(dataframe, {})) and len(df) > 0:
        comm.reply(f'For {description} of {column!r} from {dataframe!r}, please copy the following code to a cell:')
        if df[column].dtype == object and isinstance(df.iloc[0][column], str):
            code += f"{dataframe}['{prefix}_{column}'] = {str_op}"
        elif df[column].dtype == object and isinstance(df.iloc[0][column], list):
            code += f"{dataframe}['{prefix}_{column}'] = {dataframe}['{column}'].apply(lambda row: {list_op})"
        else:
            code = ""
    else:
        comm.reply(f'I could not find this the column {column!r} from the dataframe {dataframe!r}. If you know this exists and it has a string type, please copy the following code to a cell:')
        code += f"{dataframe}['{prefix}_{column}'] = {str_op}"

    comm.reply(code, type_="cell")


def transform_case_generic(case, comm, subjectstate, previousstate, matches=None):
    instructions = matches and matches.group(2) or ""

    dataframe = yield from select_dataframe(comm, re.search(r"from (dataframe )?(?P<df>.+?(?=( column )|$))", instructions))
    column = yield from select_column(comm, re.search(r"((^(?!from))|(column ))(?P<column>.+?(?=( from )|$))", instructions))
    
    apply_str_list_operation(
        comm, "transforming the case", dataframe, column, case,
        f"{dataframe}['{column}'].str.{case}()",
        f"[item.{case}() for item in row]"
    )

@statemanager
def to_lowercase_state(comm, subjectstate, previousstate, matches=None):
    yield from transform_case_generic("lower", comm, subjectstate, previousstate, matches)
    return subjectstate

@statemanager
def to_uppercase_state(comm, subjectstate, previousstate, matches=None):
    yield from transform_case_generic("upper", comm, subjectstate, previousstate, matches)
    return subjectstate


def filter_length_generic(operator, comm, subjectstate, previousstate, matches=None):
    number = matches and matches.group(1) or ""
    instructions = matches and matches.group(2) or ""

    dataframe = yield from select_dataframe(comm, re.search(r"from (dataframe )?(?P<df>.+?(?=( column )|$))", instructions))
    column = yield from select_column(comm, re.search(r"((^(?!from))|(column ))(?P<column>.+?(?=( from )|$))", instructions))
    
    if not number:
        comm.reply("Please, write the number")
        number = yield

    apply_str_list_operation(
        comm, "filtering the length", dataframe, column, "flength",
        f"{dataframe}.where({dataframe}['{column}'].str.len() {operator} {number})['{column}']",
        f"[item for item in row if len(item) {operator} {number}]"
    )



@statemanager
def minimum_length_state(comm, subjectstate, previousstate, matches=None):
    yield from filter_length_generic(">", comm, subjectstate, previousstate, matches)
    return subjectstate

@statemanager
def minimum_length_inclusive_state(comm, subjectstate, previousstate, matches=None):
    yield from filter_length_generic(">=", comm, subjectstate, previousstate, matches)
    return subjectstate

@statemanager
def maximum_length_state(comm, subjectstate, previousstate, matches=None):
    yield from filter_length_generic("<", comm, subjectstate, previousstate, matches)
    return subjectstate

@statemanager
def maximum_length_inclusive_state(comm, subjectstate, previousstate, matches=None):
    yield from filter_length_generic("<=", comm, subjectstate, previousstate, matches)
    return subjectstate

@statemanager
def range_length_state(comm, subjectstate, previousstate, matches=None):
    minimum = matches and matches.group(1) or ""
    maximum = matches and matches.group(2) or ""
    instructions = matches and matches.group(3) or ""

    dataframe = yield from select_dataframe(comm, re.search(r"from (dataframe )?(?P<df>.+?(?=( column )|$))", instructions))
    column = yield from select_column(comm, re.search(r"((^(?!from))|(column ))(?P<column>.+?(?=( from )|$))", instructions))
    
    if not minimum:
        comm.reply("Please, write the minimum number of characters")
        minimum = yield

    if not maximum:
        comm.reply("Please, write the maximum number of characters")
        maximum = yield

    apply_str_list_operation(
        comm, "filtering the length", dataframe, column, "flength",
        f"{dataframe}.where(({dataframe}['{column}'].str.len() >= {minimum}) & ({dataframe}['{column}'].str.len() <= {maximum}))['{column}']",
        f"[item for item in row if {minimum} <= len(item) <= {maximum}]"
    )
    return subjectstate

@statemanager
def remove_stopwords_state(comm, subjectstate, previousstate, matches=None):
    instructions = matches and matches.group(1) or ""

    dataframe = yield from select_dataframe(comm, re.search(r"from (dataframe )?(?P<df>.+?(?=( column )|$))", instructions))
    column = yield from select_column(comm, re.search(r"((^(?!from))|(column ))(?P<column>.+?(?=( from )|$))", instructions))

    code = ""
    if 'stopwords' not in comm.shell.user_ns:
        code = "from nltk.corpus import stopwords\nnltk.download('stopwords')\n"
    apply_str_list_operation(
        comm, "removing the stopwords of", dataframe, column, "nostop",
        f"{dataframe}.where({dataframe}['{column}'].isin(~stopwords.words()))['{column}']",
        f"[item for item in row if item not in stopwords.words()]",
        code=code,
    )
    return subjectstate


TREE = SubjectTree(
    "",
    SubjectTree(
        "Load data",
        action=load_file_state,
        regex="load data ?(.*)"
    ),
    SubjectTree(
        "Classification",
        SubjectTree(
            "Preprocessing",
            SubjectTree(
                "Select column",
                select_column=select_column_state,
                regex="select column (.+)",
                action=select_column_state
            ),
            SubjectTree(
                "Tokenize",
                regex=r"tokenize (.+)",
                action=tokenize_column_state
            ),
            SubjectTree(
                "Transform Cases",
                SubjectTree(
                    "Lowercase",
                    regex=r"transform cases? to lower ?case( of (.+))?",
                    action=to_lowercase_state
                ),
                SubjectTree(
                    "Uppercase",
                    regex=r"transform cases? to upper ?case( of (.+))?",
                    action=to_uppercase_state
                ),
                what_is_it="Transforms cases of characters in a document. \nThis operator transforms all characters in a document to either lower case or upper case, respectively. "
            ),
            SubjectTree(
                "Filter tokens by length",
                SubjectTree(
                    "Minimum Length",
                    regex=r"filter tokens with more than (\d+) characters ?(.+)?",
                    action=minimum_length_state,
                ),
                SubjectTree(
                    "Minimum Length (inclusive)",
                    regex=r"filter tokens with (\d+) characters or more ?(.+)?",
                    action=minimum_length_inclusive_state,
                ),
                SubjectTree(
                    "Maximum Length",
                    regex=r"filter tokens with less than (\d+) characters ?(.+)?",
                    action=maximum_length_state,
                ),
                SubjectTree(
                    "Maximum Length (inclusive)",
                    regex=r"filter tokens with (\d+) characters or less ?(.+)?",
                    action=maximum_length_inclusive_state,
                ),
                SubjectTree(
                    "Range",
                    regex=r"filter tokens between (\d+) and (\d+) characters ?(.+)?",
                    action=range_length_state,
                ),
            ),
            SubjectTree(
                "Remove stopwords",
                regex=r"remove stopwords (.+)",
                action=remove_stopwords_state,
                what_is_it="This operator filters English stopwords from a document by removing every token which equals a stopword from the built-in stopword list. Please note that, for this operator to work properly, every token should represent a single English word only. To obtain a document with each token representing a single word, you may tokenize a document by applying the Tokenize operator beforehand.",
                
            ),
            SubjectTree("Filter stopwords"),
        ),
        action=classification_steps_state,
        regex="do a classification ?(of column (.*))"
    ),
    
 
)


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
