
from parsy import *
import functools
import textwrap
from attrs import define, field, asdict
import attr
from attr.exceptions import NotAnAttrsClassError
from pprint import pformat
from collections.abc import Mapping
from simple_uam.util.logging import get_logger

log = get_logger(__name__)

digits = decimal_digit.at_least(1).concat()

int_p = digits.map(int)

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

def not_chars(char_list):
    """
    Parser for strings of characters not in the provided string
    """
    return not_char(char_list).at_least(1).concat()

# some chars in parens
in_parens = string('(') >> not_char("()").at_least(1).concat() << string(')')

not_space = test_char(lambda c: not c.isspace(), "not space")

not_spaces = not_space.at_least(1).concat()

def not_space_or(char_list):
    """
    Parser for characters that aren't spaces or in the list.
    """
    return test_char(
        lambda c: (c not in char_list) and not c.isspace(),
        f"char not space or in {repr(char_list)}"
    )

def not_spaces_or(char_list):
    """
    Parser for strings of characters that aren't spaces or in the list.
    """
    return not_space_or(char_list).at_least(1).concat()

def dtag(parser, key=None, **kwargs):
    """
    Tags a parser by placing it in a single element dict with the
    given key.

    Arguments:
      key: If provided will place the result of the parser in a single entry
        dict under the given key.
      **kwargs: If provided, will add the given kv pairs to the dictionary
        returned by the parser, mutually exclusive with providing a key.
        Note that these override matching keys in the result.
    """

    func = None
    if key and kwargs:
        raise RuntimeError("Cannot use dtag with both single key and kv pairs")
    elif key:
        func = lambda r: {key : r}
    else:
        func = lambda r: {**r, **kwargs}

    return parser.map(func)

Parser.dtag = dtag

def tag_alt(tag_key=None, data_key=None, data_convert=None, **alternatives):
    """
    Will apply a list of alternative parsers using their key
    as a tag.

    There are three general cases for use of this function:

    Case 1: tag_key=None, data_key=??

      Given a call like:
      ```
      tag_alt(foo=parser1, bar=parser2)
      ```

      The output will use the name for each parser as the key of the
      resulting single item dict.

      So the following are valid outputs:
      ```
      {'foo': <parser1-result>} or {'bar': <parser2-result>}
      ```

      Note: Using this with only one parameter is a good way to tag the return
      value of a parser.

    Case 2: tag_key=... , data_key=None

      Given a call like:
      ```
      tag_alt('tag', foo=parser1, bar=parser1)
      ```

      The tag will be placed *within* the return values of the parsers as so:
      ```
      {'tag': 'foo', **<parser1-result>} or {'tag': 'bar', **<parser2-result>}
      ```

      Note: This requires the output of the provided parsers are all dictionaries.

    Case 3: tag_key=..., data_key=...

      Given a call like:
      ```
      tag_alt('tag', 'data', foo=parser1, bar=parser1)
      ```

      The output will be a two item dict with the parse result in its own
      field, as so:
      ```
      {'tag': 'foo', 'data': <parser1-result>} or {'tag': 'bar', 'data': <parser2-result>}
      ```


    Arguments:
      tag_key: as above
      data_key: as above
      data_convert: If true, will convert various special input keys into
        non-string python values.

        Special keys:
          'true'/'false': Boolean value
          'none': None

        (default: True if tag_key else False)
      **alternatives: as above
    """

    if data_convert == None:
        data_convert = tag_key == None

    def convert_func(key):
        if not data_convert:
            pass
        elif key == 'true':
            return True
        elif key == 'false':
            return False
        elif key == 'none':
            return None

        return key

    tag_parser = alt(
        *[parser.tag(convert_func(key)) for key, parser in alternatives.items()]
    )

    @generate
    def tag_alt_internal_parser():
        (tag, result) = yield tag_parser

        if tag_key == None:
            return {tag: result}
        elif tag_key != None and data_key == None:
            return {tag_key : tag, **result}
        else:
            return {tag_key: tag, data_key: result}

    return tag_alt_internal_parser

def with_units(value, units = None):
    """
    Wraps a value with units information if available.
    """

    if units != None:
        return {'value': value, 'units': units}
    else:
        return value

def parser_with_units(parser, units=None):
    """
    Adds units to the result of a parser.
    """
    return parser.map(lambda v: with_units(v,units))

Parser.with_units = parser_with_units

unions = lambda l : {k : v for i in l for k , v in i.items() }

def union_many(parser, min=None, max=None, times=None):
    """
    Runs a parser many times, between min and max, and unions the results.
    """


    if min == None and max == None and times == None:
        parser = parser.many()
    elif min == None and max == None and times != None:
        parser = parser.times(times)
    elif min == None and max != None and times == None:
        parser = parser.at_most(max)
    elif min != None and max == None and times == None:
        parser = parser.at_least(min)
    elif min != None and max != None and times == None:
        parser = parser.times(min, max)
    else:
        raise RuntimeError(
            "cannot use both (min,max) and times params to union_many")

    return parser.map(merge_dicts)

Parser.union_many = union_many

def union_seq(*parsers):
    """
    Runs a set of parsers in sequence unioning all their results together.
    """

    return seq(*parsers).map(merge_dicts)

def parser_exists(parser, key=None):
    """
    Makes a parser optional and return whether or not a match occured.

    Arguments:
      key: if provided will return a dict with that key set to if there was
        a match, and other values taken from a positive result.
    """
    if key == None:
        return parser.result(True).optional(False)
    else:
        return tag_alt(key,true=parser, false=success({}))

Parser.exists = parser_exists

def parser_not_exists(parser, key=None):
    """
    Makes a parser optional and return whether or not a match failed.

    Arguments:
      key: if provided will return a dict with that key set to if there was
        a match, and other values taken from a positive result.
    """
    if key == None:
        return parser.result(False).optional(True)
    else:
        return tag_alt(key,false=parser, true=success({}))

Parser.not_exists = parser_not_exists

def collect_warnings(inp, tag='__warning__', field='warnings'):
    """
    Gets any field of the input dictionary with `__warning__` in the name
    and moves it to a new subfield named 'warnings'.
    """

    output = dict()
    warnings = dict()

    for k, v in inp.items():
        if field == k:
            warnings |= v
        elif tag in k:
            warnings[k.replace(tag,'')] = v
        else:
            output[k] = v

    if len(warnings) > 0:
        output[field] = warnings

    return output

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

def collect_dicts(*vargs):
    """
    Will collect the items in a set of dicts into lists by key.

    Result:
      A dict where each value is the list of items from the input dicts for
      that key.
    """

    output = dict()

    for d in vargs:
        for k,v in d.items():
            if k not in output:
                output[k] = list()
            output[k].append(v)

    return output


def merge_dicts(head, *vargs, splat_list=True):
    """
    Merges a set of dictionaries recursively erroring out if colliding
    non-dict values aren't equal.
    """

    # If we're given a single list as input then we splat it open
    # This lets us compose the function with alt() and many() and similar
    # parser combinators
    if splat_list\
       and len(vargs) == 0\
       and isinstance(head,list)\
       and (len(head) == 0 or isinstance(head[0],dict)):

        return merge_dicts(*head)

    if isinstance(head, dict):
        return {
            k: merge_dicts(*vs, splat_list=False)\
            for k, vs in collect_dicts(head, *vargs).items()
        }
    elif all([v == head for v in vargs]):
        return head
    else:

        log.debug(
            "Invalid input collision in merge_dicts.",
            head=head,
            vargs=vargs,
            splat_list=splat_list,
        )
        raise RuntimeError("Invalid input collision in merge_dicts.")

@generate
def format_tokenizer():
    """
    tokenizer for format_parser
    """

    lit_dol = string("$$").tag('literal_dollar')
    opt_white = string("$s?").tag('optional_whitespace')
    mand_white = string("$s").tag('mandatory_whitespace')
    parse_kwarg = string("${") >> not_char('}').at_least(1).concat().tag('parser_kwarg') << string("}")
    gen_lit = not_spaces_or('$').tag('literal_string')
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

def unformat_tokens(tokens):
    """
    Converts a list of tokens back into a string.
    """

    return ''.join([
        val if tag != 'parser_kwarg' else '${' + val + '}'
        for (tag, val) in tokens
    ])

def format_parse_single(token, strict_whitespace=False, **named_parsers):
    """
    Gets the parser for a single token.
    """

    (tag, val) = token

    # if kwarg then we want to return a dict w/ the result under that value
    if tag == 'parser_kwarg':
        return named_parsers[val].dtag(val)

    # Cases where the parser should return an empty dict
    parser = None
    if tag == 'literal_dollar':
        parser = string('$')
    elif tag == 'optional_whitespace':
        parser = whitespace.optional()
    elif tag == 'mandatory_whitespace':
        parser = whitespace
    elif tag == 'literal_string':
        parser =  string(val)
    elif tag == 'literal_whitespace' and not strict_whitespace:
        parser =  whitespace
    elif tag == 'literal_whitespace' and strict_whitespace:
        parser =  string(val)

    if parser != None:
        return parser.result({})

    # Error case
    raise RuntimeError("Invalid tokenization of format string.")

@define(hash=True)
class FormatParseExpected():
    format_str: str = field()
    remaining = field(default = None)
    expected = field(default = None)

def format_parse_tokens(ftokens,
                        strict_whitespace=False,
                        **named_parsers):
    """
    Creates a parser for a list of tokens format_parser tokens.
    Produces nicer expected messages.

    Arguments:
      ftokens: The list of tokens
      other_args: as with format_parser
    """


    # No tokens left == success
    if len(ftokens) == 0:
        return success({})

    first_token = ftokens[0]

    first_parser = format_parse_single(
        first_token,
        strict_whitespace=strict_whitespace,
        **named_parsers,
    )

    printed_tokens = lambda: unformat_tokens(ftokens)

    @Parser
    def parse_token(stream, index):

        first_result = first_parser(stream, index)

        if first_result.status:

            remaining_tokens = ftokens[1:]

            remaining_parser = format_parse_tokens(
                remaining_tokens,
                strict_whitespace=strict_whitespace,
                **named_parsers,
            )

            remaining_result = remaining_parser(stream, first_result.index)

            if remaining_result.status:

                # If both first and remaining parsers succeed union their values
                # together in the correct order
                return Result.success(
                    remaining_result.index,
                    first_result.value | remaining_result.value,
                )

            else:

                new_expected = None
                remaining_expected = remaining_result.expected
                remaining_remaining = None

                # Massage inputs to reduce nesting
                if isinstance(remaining_expected, frozenset) and \
                   len(remaining_expected) == 1:
                    remaining_expected = list(remaining_expected)[0]

                if isinstance(remaining_expected, FormatParseExpected):
                    remaining_remaining = remaining_expected.remaining
                    remaining_expected = remaining_expected.expected

                # Return further failure, ensure correct context
                return Result.failure(
                    remaining_result.furthest,
                    FormatParseExpected(
                        printed_tokens(),
                        expected=remaining_expected,
                        remaining=remaining_remaining,
                    )
                )

        else:

            first_expected = first_result.expected

            # Massage inputs to reduce nesting
            if isinstance(first_expected, frozenset) and \
               len(first_expected) == 1:
                first_expected = list(first_expected)[0]

            # Fail immediately
            return Result.failure(
                index,
                FormatParseExpected(
                    printed_tokens(),
                    expected=first_result.expected,
                ),
            )

    return parse_token

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

    used_tokens = [val for (tag, val) in ftokens if tag == 'parser_kwarg']
    missing_parsers = [val for val in used_tokens if val not in named_parsers]
    extra_parsers = [val for val in named_parsers if val not in used_tokens]

    if len(missing_parsers) > 0:
        log.info(
            "Missing parsers info",
            named_parsers=named_parsers,
            f_tokens=ftokens,
        )
        raise RuntimeError(
            f"Following parsers are missing in format_parser call: "\
            f"{missing_parsers}"
        )

    if len(extra_parsers) > 0:
        log.info(
            "Extra parsers info",
            named_parsers=named_parsers,
            f_tokens=ftokens,
        )
        raise RuntimeError(
            f"Following parsers are unused in format_parser call: "\
            f"{extra_parsers}"
        )

    return format_parse_tokens(
        ftokens,
        strict_whitespace=strict_whitespace,
        **named_parsers,
    )

def force_string_keys(val):
    """
    Walks through a JSON serializable object and casts all dictionary keys to
    strings.
    """

    if isinstance(val, list):
        return [force_string_keys(v) for v in val]
    elif isinstance(val, dict):
        return {str(k): force_string_keys(v) for k,v in val.items()}
    else:
        return val

def clean_expected(inp):
    """
    Cleans up the expected values into something more pformat-able.
    """

    is_attrs = None
    try:
        is_attrs = attr.asdict(inp)
    except NotAnAttrsClassError as err:
        pass

    inp = is_attrs if is_attrs else inp

    mapping_types = [dict]
    iterable_types = [frozenset, set, list]
    out=None

    if any([isinstance(inp,t) for t in mapping_types]):
        out = dict()
        for k,v in inp.items():
            if v != None:
                out[k] = clean_expected(v)

    elif any([isinstance(inp,t) for t in iterable_types]):
        out = [clean_expected(i) for i in inp]
        if len(out) == 1:
            out = out[0]

    else:
        out = inp

    return out

def format_expected(inp):
    """
    Formats the expected values into a more human readable string.
    """
    return pformat(clean_expected(inp), compact=True)
