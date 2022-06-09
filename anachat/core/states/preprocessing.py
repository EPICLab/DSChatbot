"""Defines interactions for preprocessing the data"""

from .utils import statemanager
from .helpers import select_dataframe_column, apply_str_list_operation

@statemanager()
def select_dataframe_state(comm, dataframe=None):
    """Selects dataframe for operations"""
    if not dataframe:
        comm.reply("Please, write the dataframe name")
        dataframe = yield
    comm.memory["dataframe"] = dataframe
    comm.reply(f'Selected dataframe {dataframe!r}')


@statemanager()
def select_column_state(comm, column=None):
    """Selects column for operations"""
    if not column:
        comm.reply("Please, write the column name")
        column = yield
    comm.memory["column"] = column
    comm.reply(f'Selected column {column!r}')


@statemanager()
def tokenize_column_state(comm, instructions=None):
    """Tokenizes column"""
    set_column = comm.memory.get("column", None) is not None
    instructions = instructions or ""
    dataframe, column = yield from select_dataframe_column(comm, instructions)

    comm.reply(f'For tokenizing {column!r} from {dataframe!r}, '
               f'please copy the following code to a cell:')
    code = ""
    if 'nltk' not in comm.shell.user_ns:
        code = "import nltk\n"

    new_column = f"tokenized_{column}"
    code += (f"{dataframe}[{new_column!r}] = {dataframe}.apply("
             f"lambda row: nltk.word_tokenize(row[{column!r}]), axis=1)")
    comm.reply(code, type_="cell")
    if set_column:
        comm.memory["column"] = new_column


def transform_case_generic(case, comm, instructions=None):
    """Transforms case"""
    set_column = comm.memory.get("column", None) is not None
    instructions = instructions or ""
    dataframe, column = yield from select_dataframe_column(comm, instructions)

    apply_str_list_operation(
        comm, "transforming the case", dataframe, column, case,
        f"{dataframe}['{column}'].str.{case}()",
        f"[item.{case}() for item in row]"
    )
    if set_column:
        comm.memory["column"] = f"{case}_{column}"


@statemanager()
def to_lowercase_state(comm, instructions=None):
    """Transforms case to lowercase"""
    yield from transform_case_generic("lower", comm, instructions)


@statemanager()
def to_uppercase_state(comm, instructions=None):
    """Transforms case to uppercase"""
    yield from transform_case_generic("upper", comm, instructions)


def filter_length_generic(operator, operator_name, comm, number=None, instructions=None):
    """Filters column by length"""
    set_column = comm.memory.get("column", None) is not None
    number = number or ""
    instructions = instructions or ""
    dataframe, column = yield from select_dataframe_column(comm, instructions)

    if not number:
        comm.reply("Please, write the number")
        number = yield

    apply_str_list_operation(
        comm, "filtering the length", dataframe, column, operator_name,
        f"{dataframe}.where({dataframe}['{column}'].str.len() {operator} {number})['{column}']",
        f"[item for item in row if len(item) {operator} {number}]"
    )
    if set_column:
        comm.memory["column"] = f"{operator_name}_{column}"


@statemanager()
def minimum_length_state(comm, number=None, instructions=None):
    """Filters column by minimum length (>)"""
    yield from filter_length_generic(">", "gt", comm, number, instructions)


@statemanager()
def minimum_length_inclusive_state(comm, number=None, instructions=None):
    """Filters column by minimum length, inclusive (>=)"""
    yield from filter_length_generic(">=", "ge", comm, number, instructions)


@statemanager()
def maximum_length_state(comm, number=None, instructions=None):
    """Filters column by maximum length (<)"""
    yield from filter_length_generic("<", "lt", comm, number, instructions)


@statemanager()
def maximum_length_inclusive_state(comm, number=None, instructions=None):
    """Filters column by minimum length, inclusive (<=)"""
    yield from filter_length_generic("<=", "le", comm, number, instructions)


@statemanager()
def range_length_state(comm, minimum=None, maximum=None, instruction=None):
    """Filters column by lenght in a range (a <= x <= b)"""
    set_column = comm.memory.get("column", None) is not None
    minimum = minimum or ""
    maximum = maximum or ""
    instructions = instruction or ""

    dataframe, column = yield from select_dataframe_column(comm, instructions)

    if not minimum:
        comm.reply("Please, write the minimum number of characters")
        minimum = yield

    if not maximum:
        comm.reply("Please, write the maximum number of characters")
        maximum = yield

    apply_str_list_operation(
        comm, "filtering the length", dataframe, column, "between",
        (f"{dataframe}.where(({dataframe}['{column}'].str.len() >= {minimum}) "
         f"& ({dataframe}['{column}'].str.len() <= {maximum}))['{column}']"),
        f"[item for item in row if {minimum} <= len(item) <= {maximum}]"
    )
    if set_column:
        comm.memory["column"] = f"between_{column}"


@statemanager()
def remove_stopwords_state(comm, instructions=None):
    """Removes stopwords from tokenized input"""
    set_column = comm.memory.get("column", None) is not None
    instructions = instructions or ""
    dataframe, column = yield from select_dataframe_column(comm, instructions)

    code = ""
    if 'stopwords' not in comm.shell.user_ns:
        code = ("from nltk.corpus import stopwords\n"
                "nltk.download('stopwords')\n"
                "words = set(stopwords.words())\n")
    apply_str_list_operation(
        comm, "removing the stopwords of", dataframe, column, "nostop",
        f"{dataframe}.where({dataframe}['{column}'].isin(~words))['{column}']",
        "[item for item in row if item not in words]",
        code=code,
    )
    if set_column:
        comm.memory["column"] = f"nostop_{column}"
