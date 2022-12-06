
from parsy import *
import functools
from simple_uam.util.logging import get_logger
log = get_logger(__name__)

digits = decimal_digit.at_least(1).concat()

@generate("scientific")
def scientific():
    """
    Parse a number in scientific notation, return a string.
    """

    sign = yield string('-').optional('')

    integral = yield digits

    fractional = yield (string('.') + digits).optional('')

    exponent = yield (char_from('Ee') + char_from('+-') + digits).optional('')

    return float(sign + integral + fractional + exponent)

def not_char(char_list):
    """
    Parser for characters not in the provided string
    """
    return test_char(lambda c: c not in char_list, f"char not in {repr(char_list)}")



# some chars in parens
in_parens = string('(') >> not_char("()").at_least(1).concat() << string(')')

not_space = test_char(lambda c: not c.isspace(), "not space")

def not_space_or(char_list):
    """
    Parser for characters that aren't spaces or in the list.
    """
    return test_char(
        lambda c: (c not in char_list) and not c.isspace(),
        f"char not space or in {repr(char_list)}"
    )

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

def to_undercase(string):
    """
    lowercases a string and replaces spaces with underscores.
    """
    return '_'.join(string.lower().split())

@generate
def format_tokenizer():
    """
    tokenizer for format_parser
    """

    lit_dol = string("$$").tag('literal_dollar')
    opt_white = string("$s?").tag('optional_whitespace')
    mand_white = string("$s").tag('mandatory_whitespace')
    parse_kwarg = string("${") >> not_char('}').at_least(1).concat().tag('parser_kwarg') << string("}")
    gen_lit = not_space.at_least(1).concat().tag('literal_string')
    gen_white = whitespace.tag('literal_whitespace')

    out = yield alt(
        lit_dol,
        opt_white,
        mand_white,
        parse_kwarg,
        gen_lit,
        gen_white,
    ).many()

    return out

def format_parser(fstring, strict_whitespace=False, **named_parsers):
    """
    Works similarly to a format string except that you can pass in parsers
    that get matched to the `${name}` flags in the string.

    Flags:
      `${name}`: Named parser argument
      `$s`: Arbitrary whitespace (mandatory)
      `$s?`: Arbitrary whitespace (optional)
      `$$`: Literal `$`

    Named Arguments:
      strict_whitespace: Should all whitespaces be interpreted as `$s` or
        literal strings?

    Returns:
      kwargs : Tuple with kwarg names and parsed values
    """

    ftokens = format_tokenizer.parse(fstring)

    @generate
    def input_parser():

        kwargs_out = dict()

        for (tag, val) in ftokens:
            if tag == 'literal_dollar':
                yield string('$')
            elif tag == 'optional_whitespace':
                yield whitespace.optional()
            elif tag == 'mandatory_whitespace':
                yield whitespace
            elif tag == 'parser_kwarg':
                kwargs_out[val] = yield named_parsers[val]
            elif tag == 'literal_string':
                yield string(val)
            elif tag == 'literal_whitespace' and not strict_whitespace:
                yield whitespace
            elif tag == 'literal_whitespace' and strict_whitespace:
                yield string(val)
            else:
                raise RuntimeError("Invalid tokenization of format string.")

        return kwargs_out

    return input_parser
