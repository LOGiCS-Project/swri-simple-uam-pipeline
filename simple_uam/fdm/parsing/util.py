
from parsy import *
from simple_uam.util.logging import get_logger
log = get_logger(__name__)

digits = decimal_digit.many().concat()

@generate("scientific")
def scientific():
    """
    Parse a number in scientific notation, return a string.
    """

    sign = yield string('-').optional('')

    integral = yield digits

    fractional = yield (string('.') + digits).optional('')

    exponent = yield (char_from('Ee') + char_from('+-') + digits).optional('')

    return sign + integral + fractional + exponent

def wrap_whitespace(parser):
    """
    Wrap a parser in optional whitespace.
    """

    @generate
    def wrapped():
        yield whitespace.optional()
        res = yield parser
        yield whitespace.optional()
        return res

    return wrapped

def wrap_blanklines(lineparser):
    """
    Wrap a line parser in optional blank lines.
    """

    @generate
    def wrapped():
        yield blank_line.many()
        res = yield lineparser
        yield blank_line.manu()
        return res

    return wrapped
