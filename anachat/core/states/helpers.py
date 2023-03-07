"""Interactions helpers"""
from __future__ import annotations
from typing import TYPE_CHECKING

import re
import sys


if TYPE_CHECKING:
    from typing import Generator, Match, Tuple, List, Any
    from ...comm.kernelcomm import KernelComm
    from ...comm.message import MessageContext, IOptionItem


def isdataframe(value: Any) -> bool:
    """Checks if value is a pandas dataframe"""
    if 'pandas' in sys.modules:
        # pylint: disable=import-outside-toplevel
        import pandas as pd
        return isinstance(value, pd.DataFrame)
    return str(type(value)) == "<class 'pandas.core.frame.DataFrame'>"


def get_dataframes(comm: KernelComm) -> Generator[str, None, None]:
    """Returns the available dataframes from the namespace"""
    for var, value in comm.shell.user_ns.items():
        if isdataframe(value):
            yield var


def select_dataframe(
    context: MessageContext,
    matches: Match[str] | None
) -> Generator[None, str, str]:
    """Extracts dataframe name from pattern matching"""
    if matches and matches.group('df'):
        dataframe = matches.group('df')
    elif context.instance.memory['dataframe']:
        dataframe = context.instance.memory['dataframe']
    else:
        options: List[IOptionItem] = [
            {'key': str(i + 1), 'label': df} for i, df in enumerate(get_dataframes(context.comm))
        ]
        if not options:
            context.reply("I could not find any dataframe in your notebook. "
                          "Please write the expression of the dataframe")
        else:
            context.reply_options(options, text="Please, select a dataframe")
        dataframe = yield
    return dataframe


def select_column(context: MessageContext, matches: Match[str] | None) -> Generator[None, str, str]:
    """Extracts column name from pattern matching"""
    if matches and matches.group('column'):
        column = matches.group('column')
        if column.startswith("column "):
            column = column[7:]
    elif context.instance.memory['column']:
        column = context.instance.memory['column']
    else:
        context.reply("Please, write the column name")
        column = yield
    return column


def select_dataframe_column(
    context: MessageContext,
    instructions: str
) -> Generator[None, str, Tuple[str, str]]:
    """Extracts dataframe and column from predefined pattern"""
    dataframe = yield from select_dataframe(
        context, re.search(r"from (dataframe )?(?P<df>.+?(?=( column )|$))", instructions)
    )
    column = yield from select_column(
        context, re.search(r"((^(?!from))|(column ))(?P<column>.+?(?=( from )|$))", instructions)
    )
    return dataframe, column


def apply_str_list_operation(
    context: MessageContext, description: str, dataframe: str, column: str,
    prefix: str, str_op: str, list_op: str, code: str=""
) -> None:
    """Applies operations for str dataframe column or list dataframe column"""
    reply_text = ""
    if column in (df := context.comm.shell.user_ns.get(dataframe, {})) and len(df) > 0:
        reply_text = (f'For {description} of {column!r} from {dataframe!r}, '
                      f'please copy the following code to a cell:')
        if df[column].dtype == object and isinstance(df.iloc[0][column], str):
            code += f"{dataframe}['{prefix}_{column}'] = {str_op}"
        elif df[column].dtype == object and isinstance(df.iloc[0][column], list):
            code += (f"{dataframe}['{prefix}_{column}'] = "
                     f"{dataframe}['{column}'].apply(lambda row: {list_op})")
        else:
            code = ""
    else:
        reply_text = (f'I could not find this the column {column!r} from the dataframe {dataframe!r}. '
                      f'If you know this exists and it has a string type, please copy the following code to a cell:')
        code += f"{dataframe}['{prefix}_{column}'] = {str_op}"

    context.reply(reply_text + f'####code#:\n{code}')
