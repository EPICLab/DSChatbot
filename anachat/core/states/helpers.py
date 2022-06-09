"""Interactions helpers"""
import re
import sys

def isdataframe(value):
    """Checks if value is a pandas dataframe"""
    if 'pandas' in sys.modules:
        # pylint: disable=import-outside-toplevel
        import pandas as pd
        return isinstance(value, pd.DataFrame)
    return str(type(value)) == "<class 'pandas.core.frame.DataFrame'>"


def get_dataframes(comm):
    """Returns the available dataframes from the namespace"""
    for var, value in comm.shell.user_ns.items():
        if isdataframe(value):
            yield var


def select_dataframe(comm, matches):
    """Extracts dataframe name from pattern matching"""
    if matches and matches.group('df'):
        dataframe = matches.group('df')
    elif comm.memory['dataframe']:
        dataframe = comm.memory['dataframe']
    else:
        options = [
            {'key': i + 1, 'label': df} for i, df in enumerate(get_dataframes(comm))
        ]
        if not options:
            comm.reply("I could not find any dataframe in your notebook. "
                       "Please write the expression of the dataframe")
        else:
            comm.reply("Please, select a dataframe")
            comm.reply(options, "options")
        dataframe = yield
    return dataframe


def select_column(comm, matches):
    """Extracts column name from pattern matching"""
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


def select_dataframe_column(comm, instructions):
    """Extracts dataframe and column from predefined pattern"""
    dataframe = yield from select_dataframe(
        comm, re.search(r"from (dataframe )?(?P<df>.+?(?=( column )|$))", instructions)
    )
    column = yield from select_column(
        comm, re.search(r"((^(?!from))|(column ))(?P<column>.+?(?=( from )|$))", instructions)
    )
    return dataframe, column


def apply_str_list_operation(
    comm, description, dataframe, column,
    prefix, str_op, list_op, code=""
):
    """Applies operations for str dataframe column or list dataframe column"""
    if column in (df := comm.shell.user_ns.get(dataframe, {})) and len(df) > 0:
        comm.reply(f'For {description} of {column!r} from {dataframe!r}, '
                   f'please copy the following code to a cell:')
        if df[column].dtype == object and isinstance(df.iloc[0][column], str):
            code += f"{dataframe}['{prefix}_{column}'] = {str_op}"
        elif df[column].dtype == object and isinstance(df.iloc[0][column], list):
            code += (f"{dataframe}['{prefix}_{column}'] = "
                     f"{dataframe}['{column}'].apply(lambda row: {list_op})")
        else:
            code = ""
    else:
        comm.reply(f'I could not find this the column {column!r} from the dataframe {dataframe!r}. '
                   f'If you know this exists and it has a string type, please copy the following code to a cell:')
        code += f"{dataframe}['{prefix}_{column}'] = {str_op}"

    comm.reply(code, type_="cell")
