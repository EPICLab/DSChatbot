"""Defines interactions for preprocessing the data"""
from __future__ import annotations
from typing import TYPE_CHECKING

from .utils import statemanager
from .helpers import select_dataframe_column, apply_str_list_operation


if TYPE_CHECKING:
    from typing import Generator
    from ...comm.context import MessageContext
    from .state import StateDefinition, StateGenerator


@statemanager()
def select_dataframe_state(
    context: MessageContext,
    dataframe: str | None=None
) -> StateGenerator:
    """Selects dataframe for operations"""
    if not dataframe:
        context.reply("Please, write the dataframe name")
        dataframe = yield
    context.comm.memory["dataframe"] = dataframe
    context.reply(f'Selected dataframe {dataframe!r}')
    return None

@statemanager()
def select_column_state(
    context: MessageContext,
    column: str | None=None
) -> StateGenerator:
    """Selects column for operations"""
    if not column:
        context.reply("Please, write the column name")
        column = yield
    context.comm.memory["column"] = column
    context.reply(f'Selected column {column!r}')
    return None


@statemanager()
def tokenize_column_state(
    context: MessageContext,
    instructions: str | None=None
) -> StateGenerator:
    """Tokenizes column"""
    set_column = context.comm.memory.get("column", None) is not None
    instructions = instructions or ""
    dataframe, column = yield from select_dataframe_column(context, instructions)

    context.reply(f'For tokenizing {column!r} from {dataframe!r}, '
                  f'please copy the following code to a cell:')
    code = ""
    if 'nltk' not in context.comm.shell.user_ns:
        code = "import nltk\n"

    new_column = f"tokenized_{column}"
    code += (f"{dataframe}[{new_column!r}] = {dataframe}.apply("
             f"lambda row: nltk.word_tokenize(row[{column!r}]), axis=1)")
    context.reply(code, type_="cell")
    if set_column:
        context.comm.memory["column"] = new_column
    return None


def transform_case_generic(
    case: str,
    context: MessageContext,
    instructions: str | None=None
) -> Generator[None, str, None]:
    """Transforms case"""
    set_column = context.comm.memory.get("column", None) is not None
    instructions = instructions or ""
    dataframe, column = yield from select_dataframe_column(context, instructions)

    apply_str_list_operation(
        context, "transforming the case", dataframe, column, case,
        f"{dataframe}['{column}'].str.{case}()",
        f"[item.{case}() for item in row]"
    )
    if set_column:
        context.comm.memory["column"] = f"{case}_{column}"


@statemanager()
def to_lowercase_state(
    context: MessageContext,
    instructions: str | None=None
) -> StateGenerator:
    """Transforms case to lowercase"""
    yield from transform_case_generic("lower", context, instructions)
    return None


@statemanager()
def to_uppercase_state(
    context: MessageContext,
    instructions: str | None=None
) -> StateGenerator:
    """Transforms case to uppercase"""
    yield from transform_case_generic("upper", context, instructions)
    return None


def filter_length_generic(
    operator: str,
    operator_name: str,
    context: MessageContext,
    number: str | None=None,
    instructions: str | None=None
) -> Generator[None, str, None]:
    """Filters column by length"""
    set_column = context.comm.memory.get("column", None) is not None
    number = number or ""
    instructions = instructions or ""
    dataframe, column = yield from select_dataframe_column(context, instructions)

    if not number:
        context.reply("Please, write the number")
        number = yield

    apply_str_list_operation(
        context, "filtering the length", dataframe, column, operator_name,
        f"{dataframe}.where({dataframe}['{column}'].str.len() {operator} {number})['{column}']",
        f"[item for item in row if len(item) {operator} {number}]"
    )
    if set_column:
        context.comm.memory["column"] = f"{operator_name}_{column}"
    return None


@statemanager()
def minimum_length_state(
    context: MessageContext,
    number: str | None=None,
    instructions: str | None=None
) -> StateGenerator:
    """Filters column by minimum length (>)"""
    yield from filter_length_generic(">", "gt", context, number, instructions)
    return None


@statemanager()
def minimum_length_inclusive_state(
    context: MessageContext,
    number: str | None=None,
    instructions: str | None=None
) -> StateGenerator:
    """Filters column by minimum length, inclusive (>=)"""
    yield from filter_length_generic(">=", "ge", context, number, instructions)
    return None


@statemanager()
def maximum_length_state(
    context: MessageContext,
    number: str | None=None,
    instructions: str | None=None
) -> StateGenerator:
    """Filters column by maximum length (<)"""
    yield from filter_length_generic("<", "lt", context, number, instructions)
    return None


@statemanager()
def maximum_length_inclusive_state(
    context: MessageContext,
    number: str | None=None,
    instructions: str | None=None
) -> StateGenerator:
    """Filters column by minimum length, inclusive (<=)"""
    yield from filter_length_generic("<=", "le", context, number, instructions)
    return None


@statemanager()
def range_length_state(
    context: MessageContext,
    minimum: str | None=None,
    maximum: str | None=None,
    instruction: str | None=None
) -> StateGenerator:
    """Filters column by lenght in a range (a <= x <= b)"""
    set_column = context.comm.memory.get("column", None) is not None
    minimum = minimum or ""
    maximum = maximum or ""
    instructions = instruction or ""

    dataframe, column = yield from select_dataframe_column(context, instructions)

    if not minimum:
        context.reply("Please, write the minimum number of characters")
        minimum = yield

    if not maximum:
        context.reply("Please, write the maximum number of characters")
        maximum = yield

    apply_str_list_operation(
        context, "filtering the length", dataframe, column, "between",
        (f"{dataframe}.where(({dataframe}['{column}'].str.len() >= {minimum}) "
         f"& ({dataframe}['{column}'].str.len() <= {maximum}))['{column}']"),
        f"[item for item in row if {minimum} <= len(item) <= {maximum}]"
    )
    if set_column:
        context.comm.memory["column"] = f"between_{column}"
    return None


@statemanager()
def remove_stopwords_state(
    context: MessageContext,
    instructions: str | None=None
) -> StateGenerator:
    """Removes stopwords from tokenized input"""
    set_column = context.comm.memory.get("column", None) is not None
    instructions = instructions or ""
    dataframe, column = yield from select_dataframe_column(context, instructions)

    code = ""
    if 'stopwords' not in context.comm.shell.user_ns:
        code = ("from nltk.corpus import stopwords\n"
                "nltk.download('stopwords')\n"
                "words = set(stopwords.words())\n")
    apply_str_list_operation(
        context, "removing the stopwords of", dataframe, column, "nostop",
        f"{dataframe}.where({dataframe}['{column}'].isin(~words))['{column}']",
        "[item for item in row if item not in words]",
        code=code,
    )
    if set_column:
        context.comm.memory["column"] = f"nostop_{column}"
    return None
