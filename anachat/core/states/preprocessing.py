"""Defines interactions for preprocessing the data"""

from .utils import statemanager
from .helpers import select_dataframe_column, apply_str_list_operation

@statemanager()
def select_dataframe_state(comm, reply_to, dataframe=None):
    """Selects dataframe for operations"""
    if not dataframe:
        comm.reply("Please, write the dataframe name", reply=reply_to)
        dataframe = yield
    comm.memory["dataframe"] = dataframe
    comm.reply(f'Selected dataframe {dataframe!r}', reply=reply_to)


@statemanager()
def select_column_state(comm, reply_to, column=None):
    """Selects column for operations"""
    if not column:
        comm.reply("Please, write the column name", reply=reply_to)
        column = yield
    comm.memory["column"] = column
    comm.reply(f'Selected column {column!r}', reply=reply_to)


@statemanager()
def tokenize_column_state(comm, reply_to, instructions=None):
    """Tokenizes column"""
    set_column = comm.memory.get("column", None) is not None
    instructions = instructions or ""
    dataframe, column = yield from select_dataframe_column(comm, reply_to, instructions)

    comm.reply(f'For tokenizing {column!r} from {dataframe!r}, '
               f'please copy the following code to a cell:', reply=reply_to)
    code = ""
    if 'nltk' not in comm.shell.user_ns:
        code = "import nltk\n"

    new_column = f"tokenized_{column}"
    code += (f"{dataframe}[{new_column!r}] = {dataframe}.apply("
             f"lambda row: nltk.word_tokenize(row[{column!r}]), axis=1)")
    comm.reply(code, type_="cell", reply=reply_to)
    if set_column:
        comm.memory["column"] = new_column


def transform_case_generic(case, comm, reply_to, instructions=None):
    """Transforms case"""
    set_column = comm.memory.get("column", None) is not None
    instructions = instructions or ""
    dataframe, column = yield from select_dataframe_column(comm, reply_to, instructions)

    apply_str_list_operation(
        comm, reply_to, "transforming the case", dataframe, column, case,
        f"{dataframe}['{column}'].str.{case}()",
        f"[item.{case}() for item in row]"
    )
    if set_column:
        comm.memory["column"] = f"{case}_{column}"


@statemanager()
def to_lowercase_state(comm, reply_to, instructions=None):
    """Transforms case to lowercase"""
    yield from transform_case_generic("lower", comm, reply_to, instructions)


@statemanager()
def to_uppercase_state(comm, reply_to, instructions=None):
    """Transforms case to uppercase"""
    yield from transform_case_generic("upper", comm, reply_to, instructions)


def filter_length_generic(operator, operator_name, comm, reply_to, number=None, instructions=None):
    """Filters column by length"""
    set_column = comm.memory.get("column", None) is not None
    number = number or ""
    instructions = instructions or ""
    dataframe, column = yield from select_dataframe_column(comm, reply_to, instructions)

    if not number:
        comm.reply("Please, write the number", reply=reply_to)
        number = yield

    apply_str_list_operation(
        comm, reply_to, "filtering the length", dataframe, column, operator_name,
        f"{dataframe}.where({dataframe}['{column}'].str.len() {operator} {number})['{column}']",
        f"[item for item in row if len(item) {operator} {number}]"
    )
    if set_column:
        comm.memory["column"] = f"{operator_name}_{column}"


@statemanager()
def minimum_length_state(comm, reply_to, number=None, instructions=None):
    """Filters column by minimum length (>)"""
    yield from filter_length_generic(">", "gt", comm, reply_to, number, instructions)


@statemanager()
def minimum_length_inclusive_state(comm, reply_to, number=None, instructions=None):
    """Filters column by minimum length, inclusive (>=)"""
    yield from filter_length_generic(">=", "ge", comm, reply_to, number, instructions)


@statemanager()
def maximum_length_state(comm, reply_to, number=None, instructions=None):
    """Filters column by maximum length (<)"""
    yield from filter_length_generic("<", "lt", comm, reply_to, number, instructions)


@statemanager()
def maximum_length_inclusive_state(comm, reply_to, number=None, instructions=None):
    """Filters column by minimum length, inclusive (<=)"""
    yield from filter_length_generic("<=", "le", comm, reply_to, number, instructions)


@statemanager()
def range_length_state(comm, reply_to, minimum=None, maximum=None, instruction=None):
    """Filters column by lenght in a range (a <= x <= b)"""
    set_column = comm.memory.get("column", None) is not None
    minimum = minimum or ""
    maximum = maximum or ""
    instructions = instruction or ""

    dataframe, column = yield from select_dataframe_column(comm, reply_to, instructions)

    if not minimum:
        comm.reply("Please, write the minimum number of characters", reply=reply_to)
        minimum = yield

    if not maximum:
        comm.reply("Please, write the maximum number of characters", reply=reply_to)
        maximum = yield

    apply_str_list_operation(
        comm, reply_to, "filtering the length", dataframe, column, "between",
        (f"{dataframe}.where(({dataframe}['{column}'].str.len() >= {minimum}) "
         f"& ({dataframe}['{column}'].str.len() <= {maximum}))['{column}']"),
        f"[item for item in row if {minimum} <= len(item) <= {maximum}]"
    )
    if set_column:
        comm.memory["column"] = f"between_{column}"


@statemanager()
def remove_stopwords_state(comm, reply_to, instructions=None):
    """Removes stopwords from tokenized input"""
    set_column = comm.memory.get("column", None) is not None
    instructions = instructions or ""
    dataframe, column = yield from select_dataframe_column(comm, reply_to, instructions)

    code = ""
    if 'stopwords' not in comm.shell.user_ns:
        code = ("from nltk.corpus import stopwords\n"
                "nltk.download('stopwords')\n"
                "words = set(stopwords.words())\n")
    apply_str_list_operation(
        comm, reply_to, "removing the stopwords of", dataframe, column, "nostop",
        f"{dataframe}.where({dataframe}['{column}'].isin(~words))['{column}']",
        "[item for item in row if item not in words]",
        code=code,
    )
    if set_column:
        comm.memory["column"] = f"nostop_{column}"
