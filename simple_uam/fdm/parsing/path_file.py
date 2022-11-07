
from parsy import *
from .line_parser import *
from .util import *

from simple_uam.util.logging import get_logger

log = get_logger(__name__)

known_headers = [
    'Time',
    'X',
    'Xpath',
    'Xpathdot',
    'Xdiff',
    'Y',
    'Ypath',
    'Ydiff',
    'Z',
    'Zpath',
    'Zdiff',
    'Longitude err',
    'L1_error',
    'L1_error_max',
    'L1_error_int',
    'q0',
    'q1',
    'q2',
    'q3',
    'Phi',
    'Theta',
    'Psi',
    'norm q - 1',
]

column_header = (string_from(*known_headers) | regex(r'[_+\-A-Za-z0-9]').at_least(1))

header_row = wrap_whitespace(column_header.sep_by(whitespace))

numeric_row = wrap_whitespace(scientific.sep_by(whitespace))

@generate
def path_data_parser():
    """
    Create a line parser for a path input file.

    Returns a tuple of (output, fieldnames)
    """

    yield blank_line.many()
    header = yield parse_line(header_row)
    data = yield parse_line(numeric_row).many()
    yield blank_line.many()

    output = list()
    field_set = list()

    for row in data:

        if len(row) != len(header):
            log.warning(
                "Header and data rows don't match up when parsing path file.",
                header_entries=header,
                row_entries=row,
            )

        row_entry = dict()

        for (ind, val) in enumerate(row):

            label = str(ind)

            if ind < len(header):
                label = header[ind]

            if label not in field_set:
                field_set.append(label)

            row_entry[label] = val

        output.append(row_entry)

    field_names = list()

    for field in known_headers:
        if field in field_set and field not in field_names:
            field_names.append(field)

    for field in field_set:
        if field not in field_names:
            field_names.append(field)


    return tuple([output, field_names])

def parse_path_data(string):
    """
    Parses a path input string, outputs

    Returns:
      output: list of dicts of each row of data in the file
      fieldnames: list of all fieldnames used in the file
    """

    return run_lineparser(path_data_parser, string)
