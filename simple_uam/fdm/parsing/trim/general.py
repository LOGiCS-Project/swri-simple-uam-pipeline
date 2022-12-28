from parsy import *
from copy import deepcopy, copy
from ..line_parser import *
from ..block_parser import *
from ..util import *
from .shared import *
from .summary import *
from simple_uam.util.logging import get_logger
log = get_logger(__name__)

prefix_lines_parser = static_lines(
    """
    This routine finds steady solutions for general trim states, including turns.
	A steady state (trimmed) flight condition is achieved when UVWdot and PQRdot are zero.
	It is usually assumed that the flight direction is X.
    """
)

general_trim_prefix_block = parse_block(
    'general_trim_prefix',
    prefix_lines_parser.result(None),
)

motion_lines_parser = turning_motion_lines_parser.dtag(state_type='turning')

finished_lmdiff_line_parser = parse_strip_line(
    format_parser(
        'Finished lmdif1 call; info = ${lmdif1_info} '\
        '(should be 1, 2 or 3; see MINPACK documentation)',
        lmdif1_info=int_p,
    )
)

simplex_iter_line_parser = parse_strip_line(
    format_parser(
        'Nonlinear  simplex invoked: iterations = ${iterations}',
        iterations=int_p,
    )
).exists('invoked')

@generate
def trim_state_prefix_lines_parser():

    output = dict()

    output |= yield motion_lines_parser
    output |= yield lwa_size_warning_line_parser.optional({})
    output |= yield finished_lmdiff_line_parser
    output |= yield simplex_iter_line_parser.dtag('nonlinear_simplex')

    return output

general_trim_state_prefix_block_parser = parse_block(
    'general_trim_state_prefix',
    trim_state_prefix_lines_parser.map(collect_warnings)
)

@generate
def trim_state_lines_parser():

    output = dict()

    output |= yield trim_state_prefix_lines_parser
    output |= yield trim_state_vars_lines_parser
    output |= yield trim_state_battery_info_lines_parser
    output |= yield trim_state_controls_lines_parser.exists('successful')

    return output

general_trim_state_block_parser = parse_block(
    'general_trim_state',
    trim_state_lines_parser.map(collect_warnings)
)

trim_state_count_line_parser = parse_strip_line(
    trim_state_count_str_parser
)

@generate
def summary_lines_parser():

    output = dict()
    output |= yield trim_state_count_line_parser
    output |= yield control_state_count_line_parser
    yield blank_line.many()
    yield summary_prefix_header_lines
    yield blank_line.many()
    output |= yield summary_turning_radius_line_parser
    yield blank_line.many()
    output |= yield summary_table_lines_parser

    return output

general_trim_summary_block_parser = parse_block(
    'general_trim_summary',
    summary_lines_parser.map(collect_warnings)
)

@generate
def general_trim_lines_parser():

    output = dict()

    yield prefix_lines_parser
    yield blank_line.many()
    output |= yield trim_state_lines_parser\
        .map(collect_warnings)\
        .sep_by(blank_lines)\
        .dtag('trim_states')
    yield blank_line.many()
    output |= yield summary_lines_parser

    return output

general_trim_block_parser = parse_block(
    'general_trim',
    general_trim_lines_parser.map(collect_warnings)
)
