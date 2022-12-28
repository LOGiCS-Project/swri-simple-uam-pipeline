
from parsy import *
from .util import *
import textwrap
from copy import deepcopy, copy
from attrs import define, field
import attrs
from simple_uam.util.logging import get_logger
log = get_logger(__name__)

@define(hash=True)
class Expected():
    expected = field()
    at_char : int = field()

def parse_line(str_parser):
    """
    Converts a parser for a string into a parser that matches a single
    input line.
    """

    @Parser
    def run_line(lines, lineno):

        if lineno >= len(lines):
            return Result.failure(lineno, f'No more lines in input.')


        line = lines[lineno]
        result = copy((str_parser << eof)(line, 0))
        if result.status:

            # log.debug(
            #     "Successsful single line parse of.",
            #     parser_module=str_parser.__module__,
            #     lineno=lineno,
            #     line=lines[lineno],
            # )

            return Result.success(lineno + 1, result.value)
        else:
            expected = Expected(
                expected = result.expected,
                at_char = result.furthest,
            )
            return Result.failure(lineno, expected)

    return run_line

def parse_strip_line(str_parser):
   """
   Parses a line ignoring whitespace on either side.
   """
   return parse_line(wrap_whitespace(str_parser))

raw_line = parse_line(any_char.many().concat())

blank_line = parse_line(whitespace | string(""))

blank_lines = blank_line.at_least(1)

def run_lineparser(parser, string):
    """
    Splits a string into lines and runs a line parser.
    """

    lines = string.splitlines()

    return parser.parse(lines)

def wrap_blanklines(lineparser):
    """
    Wrap a line parser in optional blank lines.
    """

    @generate
    def wrapped():
        yield blank_line.many()
        res = yield lineparser
        yield blank_line.many()
        return res

    return wrapped

def static_lines(input):
    """
    Parses a multiline string as a line parser.

    Ignores whitespace surrounding each line.
    """

    lines = [i.strip() for i in input.strip().splitlines()]

    @generate
    def lines_parser():
        for l in lines:
            if l.strip() == "" or l.isspace():
                yield blank_line
            else:
                yield parse_strip_line(string(l))

    return lines_parser
