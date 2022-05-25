"""Defines interactions for preprocessing the data"""

import re
from .helpers import select_dataframe_column, apply_str_list_operation
from ..states import SubjectTree, statemanager

@statemanager
def select_column_state(comm, subjectstate, previousstate, matches=None):
    """Selects column for operations"""
    if matches and matches.group(1):
        column = matches.group(1)
    else:
        comm.reply("Please, write the column name")
        column = yield
    comm.memory["column"] = column
    comm.reply(f'Selected column {column!r}')
    return subjectstate

@statemanager
def tokenize_column_state(comm, subjectstate, previousstate, matches=None):
    """Tokenizes column"""
    instructions = matches and matches.group(1) or ""
    dataframe, column = yield from select_dataframe_column(comm, instructions)

    comm.reply(f'For tokenizing {column!r} from {dataframe!r}, please copy the following code to a cell:')
    code = ""
    if 'nltk' not in comm.shell.user_ns:
        code = "import nltk\n"

    code += f"{dataframe}['tokenized_{column}'] = {dataframe}.apply(lambda row: nltk.word_tokenize(row[{column!r}]), axis=1)"
    comm.reply(code, type_="cell")
    return subjectstate


def transform_case_generic(case, comm, subjectstate, previousstate, matches=None):
    """Transforms case"""
    instructions = matches and matches.group(2) or ""
    dataframe, column = yield from select_dataframe_column(comm, instructions)

    apply_str_list_operation(
        comm, "transforming the case", dataframe, column, case,
        f"{dataframe}['{column}'].str.{case}()",
        f"[item.{case}() for item in row]"
    )


@statemanager
def to_lowercase_state(comm, subjectstate, previousstate, matches=None):
    """Transforms case to lowercase"""
    yield from transform_case_generic("lower", comm, subjectstate, previousstate, matches)
    return subjectstate

@statemanager
def to_uppercase_state(comm, subjectstate, previousstate, matches=None):
    """Transforms case to uppercase"""
    yield from transform_case_generic("upper", comm, subjectstate, previousstate, matches)
    return subjectstate


def filter_length_generic(operator, comm, subjectstate, previousstate, matches=None):
    """Filters column by length"""
    number = matches and matches.group(1) or ""
    instructions = matches and matches.group(2) or ""
    dataframe, column = yield from select_dataframe_column(comm, instructions)

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
    """Filters column by minimum length (>)"""
    yield from filter_length_generic(">", comm, subjectstate, previousstate, matches)
    return subjectstate

@statemanager
def minimum_length_inclusive_state(comm, subjectstate, previousstate, matches=None):
    """Filters column by minimum length, inclusive (>=)"""
    yield from filter_length_generic(">=", comm, subjectstate, previousstate, matches)
    return subjectstate

@statemanager
def maximum_length_state(comm, subjectstate, previousstate, matches=None):
    """Filters column by maximum length (<)"""
    yield from filter_length_generic("<", comm, subjectstate, previousstate, matches)
    return subjectstate

@statemanager
def maximum_length_inclusive_state(comm, subjectstate, previousstate, matches=None):
    """Filters column by minimum length, inclusive (<=)"""
    yield from filter_length_generic("<=", comm, subjectstate, previousstate, matches)
    return subjectstate

@statemanager
def range_length_state(comm, subjectstate, previousstate, matches=None):
    """Filters column by lenght in a range (a <= x <= b)"""
    minimum = matches and matches.group(1) or ""
    maximum = matches and matches.group(2) or ""
    instructions = matches and matches.group(3) or ""

    dataframe, column = yield from select_dataframe_column(comm, instructions)

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
    """Removes stopwords from tokenized input"""
    instructions = matches and matches.group(1) or ""

    dataframe, column = yield from select_dataframe_column(comm, instructions)

    code = ""
    if 'stopwords' not in comm.shell.user_ns:
        code = "from nltk.corpus import stopwords\nnltk.download('stopwords')\n"
    apply_str_list_operation(
        comm, "removing the stopwords of", dataframe, column, "nostop",
        f"{dataframe}.where({dataframe}['{column}'].isin(~stopwords.words()))['{column}']",
        "[item for item in row if item not in stopwords.words()]",
        code=code,
    )
    return subjectstate


PREPROCESSING_SUBTREE = SubjectTree(
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
)
