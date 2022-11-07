
from parsy import *
from simple_uam.util.logging import get_logger
log = get_logger(__name__)
def parse_line(str_parser):
    """
    Converts a parser for a string into a parser that matches a single
    input line.
    """

    @Parser
    def run_line(lines, lineno):


        if lineno >= len(lines):
            return Result.failure(lineno, f'No more lines in input.')

        # log.info(
        #     "Running single line parse of.",
        #     parser_module=str_parser.__module__,
        #     lineno=lineno,
        #     line=lines[lineno],
        # )

        line = lines[lineno]
        try:
            result = str_parser.parse(line)
            return Result.success(lineno + 1, result)
        except ParseError as err:
            return Result.failure(lineno, repr(err))

    return run_line

raw_line = parse_line(any_char.many().concat())

blank_line = parse_line(whitespace)

def run_lineparser(parser, string):
    """
    Splits a string into lines and runs a line parser.
    """

    lines = string.splitlines()

    return parser.parse(lines)
