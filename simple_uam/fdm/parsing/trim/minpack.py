from parsy import *
from copy import deepcopy, copy
from ..line_parser import *
from ..block_parser import *
from ..util import *
from .shared import *
from .summary import *
from simple_uam.util.logging import get_logger
log = get_logger(__name__)

prefix_static_lines = static_lines(
    """
    This routine finds steady solutions for lateral speeds of 0 to 50 m/s (Unorth).
    (If steady climbing is desired, set the appropriate wind speed Wdwind (positive down)).
    A steady state (trimmed) flight condition is achieved when UVWdot and PQRdot are zero.
    It is assumed that the flight direction is X and there is no yaw (psi = 0) or roll (phi = 0).
    Motor amps also includes amps lost in the ESC.
    """
)


@generate
def aircraft_simplex_str_parser():
    """
    parses lines like:
    ```
    aircraft%simplex =   2 (0 = minpack/simplex + previous convergence, 1 = simplex + previous convergence, 2 = simplex + 0.5 start).
    ```
    """

    def_parser = format_parser(
        '${num}$s?=$s?${definition}',
        num=int_p,
        definition=not_chars(",()"),
    )

    def_sep = wrap_whitespace(string(','))

    result = yield format_parser(
        "aircraft%simplex = ${a_simp} (${definitions}).",
        a_simp=int_p,
        definitions=def_parser.sep_by(def_sep),
    )

    a_simp = result['a_simp']
    definition = None
    for defn in result['definitions']:
        if defn['num'] == a_simp:
            definition = defn['definition']
            break

    output = {'value': a_simp}
    if definition:
        output['definition'] = definition

    return output

aircraft_simplex_line_parser = parse_strip_line(
    aircraft_simplex_str_parser
).dtag('aircraft_simplex')

@generate
def prefix_lines_parser():
    """
    Parses the prefix of a set of minpack_trim blocks, like:
    ```
    This routine finds steady solutions for lateral speeds of 0 to 50 m/s (Unorth).
    (If steady climbing is desired, set the appropriate wind speed Wdwind (positive down)).
    A steady state (trimmed) flight condition is achieved when UVWdot and PQRdot are zero.
    It is assumed that the flight direction is X and there is no yaw (psi = 0) or roll (phi = 0).
    Motor amps also includes amps lost in the ESC.
    aircraft%simplex =   2 (0 = minpack/simplex + previous convergence, 1 = simplex + previous convergence, 2 = simplex + 0.5 start).
    ```
    """

    output = dict()
    yield prefix_static_lines
    output |= yield aircraft_simplex_line_parser

    return output

minpack_trim_prefix_block = parse_block(
    'minpack_trim_prefix',  prefix_lines_parser
)

motion_lines_parser = tag_alt(
    'state_type',
    lateral=lateral_motion_line_parser,
    turning=turning_motion_lines_parser,
)

padding_line_parser = parse_strip_line(
    format_parser(
        'It was necessary to make m = n for MINPACK; '\
        'original n > m = ${original_n} ${original_m}',
        original_n = int_p,
        original_m = int_p,
    )
).dtag('__warning__minpack_padding_needed')

used_str_parser = alt(
    string('Y').result(True),
    string('N').result(False),
)

logical_str_parser = alt(
    string('T').result(True),
    string('F').result(False),
)

minpack_jeq_pass_line_parser = parse_strip_line(
    format_parser(
        'MINPACK       max xd, fdcost, previous, used  '\
        '${max_xd} ${fdcost} ${used}',
        max_xd= scientific,
        fdcost=scientific,
        used=used_str_parser,
    )
)

minpack_jneq_pass_line_parser = parse_strip_line(
    format_parser(
        'MINPACK       max xd, fdcost, previous, used  '\
        '${max_xd} ${fdcost} ${previous} ${used}',
        max_xd=scientific,
        fdcost=scientific,
        previous=logical_str_parser,
        used=used_str_parser,
    )
)

minpack_pass_line_parser = tag_alt(
    'j_eq_zero',
    true=minpack_jeq_pass_line_parser,
    false=minpack_jneq_pass_line_parser,
)

simplex_pass_line_parser = parse_strip_line(
    format_parser(
        'SIMPLEX pass, max xd, fdcost, previous, used, iter '\
        '${simplex_pass} ${max_xd} ${fdcost} ${previous} ${used} ${iteration}',
        simplex_pass=int_p,
        max_xd=scientific,
        fdcost=scientific,
        previous=logical_str_parser,
        used=used_str_parser,
        iteration=int_p,
    )
)
"""
Parses lines like:
```
SIMPLEX pass, max xd, fdcost, previous, used, iter   1 -1.611793669520136E-04  7.751070881881508E-06 F Y   511
```
"""

opt_pass_line_parser = tag_alt(
    'pass_type',
    minpack=minpack_pass_line_parser,
    simplex=simplex_pass_line_parser,
)

opt_passes_lines_parser = opt_pass_line_parser\
    .at_least(1)\
    .dtag('optimization_passes')

finished_minpack_lmdiff_line_parser = parse_strip_line(
    format_parser(
        'Finished  MINPACK lmdif1 call; info = ${lmdif1_info} '\
        '(should be 1, 2 or 3; see MINPACK documentation)',
        lmdif1_info=int_p,
    )
)
"""
Parses lines like:
```
Finished  MINPACK lmdif1 call; info =  0 (should be 1, 2 or 3; see MINPACK documentation)
```
"""

simplex_iter_line_parser = parse_strip_line(
    format_parser(
        'Nonlinear SIMPLEX invoked ${invocations} '\
        'time(s): total iterations = ${iterations}',
        invocations=int_p,
        iterations=int_p,
    )
).exists('invoked').dtag('nonlinear_simplex')
"""
Parses lines like:
```
Nonlinear SIMPLEX invoked 1 time(s): total iterations =   511
```
"""

@generate
def fdm_trim_state_passes_lines_parser():

    output = dict()

    output |= yield lwa_size_warning_line_parser.optional({})
    output |= yield opt_passes_lines_parser
    output |= yield finished_minpack_lmdiff_line_parser
    output |= yield simplex_iter_line_parser

    return output

user_trim_state_prefix_line_parser = parse_strip_line(
    format_parser('User specified trim state')
)

user_trim_state_warning_line_parser = parse_strip_line(
    format_parser(
        'Warning: Unorth .ne. trim speed '\
        '${u_north} ${trim_speed}',
        u_north=scientific,
        trim_speed=scientific,
    )
).dtag('__warning__user_trim_state_velocity_inconsistent')

@generate
def user_trim_state_passes_lines_parser():

    output = dict()

    yield user_trim_state_prefix_line_parser
    output |= yield user_trim_state_warning.optional({})

    return output

@generate
def trim_state_prefix_lines_parser():

    output = dict()

    output |= yield motion_lines_parser
    output |= yield padding_line_parser.optional({})

    output |= yield tag_alt(
        'state_source',
        user=user_trim_state_passes_lines_parser,
        fdm=fdm_trim_state_passes_lines_parser,
    )

    return output

minpack_trim_state_prefix_block_parser = parse_block(
    'minpack_trim_state_prefix',
    trim_state_prefix_lines_parser.map(collect_warnings)
)

@generate
def trim_state_lines_parser():

    output = dict()

    output |= yield trim_state_prefix_lines_parser
    output |= yield trim_state_vars_lines_parser
    output |= yield battery_info_lines_parser
    output |= yield trim_state_controls_lines_parser.exists('successful')

    return output

minpack_trim_state_block_parser = parse_block(
    'minpack_trim_state',
    trim_state_lines_parser.map(collect_warnings)
)

trim_state_count_line_parser = parse_strip_line(
    trim_state_count_str_parser << trim_state_count_minpack_suffix_str_parser
)

minpack_summary_prefix_header_lines = static_lines(
    """
    If no trim state is found, at the far right is shown the maximum of the accelerations and the weighted cost used by simplex.
    I.e., if all UVWPQR derivatives are less than the acceleration tolerance (in absolute value) a trim state is found.
    """
)

@generate
def acceleration_tolerance_str_parser():
    """
    parses lines like:
    ```
    The acceleration tolerance is   1.0000000000000000E-002 m|r/s^2 (default 0.01 m/s^2).
    ```
    """

    fstring = "The acceleration tolerance is ${value} ${units} "\
        "(default ${default_value} ${default_units})."

    result = yield format_parser(
        fstring,
        value=scientific,
        units=not_space.at_least(1).concat(),
        default_value=scientific,
        default_units=not_space_or("()").at_least(1).concat(),
    )

    return {
        'value': result['value'],
        'units': result['units'],
        'default': {
            'value': result['default_value'],
            'units': result['default_units'],
        },
    }

acceleration_tolerance_line_parser = parse_strip_line(
    acceleration_tolerance_str_parser
).dtag('acceleration_tolerance')

max_no_warning_distance_line_parser = parse_strip_line(
    format_parser(
        'Of all cases, maximum no-warning distance was at '\
        'speed ${speed} m/s with distance   ${distance} m',
        speed=scientific.with_units('m/s'),
        distance=scientific.with_units('m'),
    )
).dtag('max_no_warning_distance')

max_no_warning_speed_line_parser = parse_strip_line(
    format_parser(
        'Of all cases, maximum no-warning speed was a '\
        'speed of ${speed} m/s with distance   ${distance} m',
        speed=scientific.with_units('m/s'),
        distance=scientific.with_units('m'),
    )
).dtag('max_no_warning_speed')

@generate
def summary_lines_parser():

    output = dict()
    output |= yield trim_state_count_line_parser
    output |= yield control_state_count_line_parser
    yield blank_line.many()
    yield summary_prefix_header_lines
    yield minpack_summary_prefix_header_lines
    output |= yield acceleration_tolerance_line_parser
    yield blank_line.many()
    output |= yield summary_turning_radius_line_parser.optional({})
    yield blank_line.many()
    output |= yield summary_table_lines_parser
    yield blank_line.many()
    output |= yield max_no_warning_distance_line_parser
    output |= yield max_no_warning_speed_line_parser

    return output

minpack_trim_summary_block_parser = parse_block(
    'minpack_trim_summary',
    summary_lines_parser.map(collect_warnings)
)

@generate
def minpack_trim_lines_parser():

    output = dict()

    output |= yield prefix_lines_parser
    yield blank_line.many()
    output |= yield trim_state_lines_parser\
        .map(collect_warnings)\
        .sep_by(blank_lines)\
        .dtag('trim_states')
    yield blank_line.many()
    output |= yield summary_lines_parser

    return output

minpack_trim_block_parser = parse_block(
    'minpack_trim',
    minpack_trim_lines_parser.map(collect_warnings)
)
