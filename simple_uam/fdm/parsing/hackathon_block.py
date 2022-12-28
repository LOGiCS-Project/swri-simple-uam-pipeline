
from parsy import *
from .line_parser import *
from .block_parser import *
from .util import *
from .misc_vars_block import *
from .path_result_block import *
from simple_uam.util.logging import get_logger
from attrs import define, field
log = get_logger(__name__)

hackathon_open_line_parser = parse_strip_line(
    format_parser(
        "Hackathon   ${hackathon}",
        hackathon = int_p
    )
)

flight_path_line_parser = parse_strip_line(
    format_parser(
        "Path performance, flight path            ${flight_path}",
        flight_path = int_p
    )
)

@generate
def hackathon_open_lines_parser():
    output = dict()
    output |= yield hackathon_open_line_parser
    output |= yield flight_path_line_parser
    return output

hackathon_open_block_parser = parse_block('hackathon_open', hackathon_open_lines_parser)

@generate
def state_table_lines_parser():
    """
    Parses blocks like:
    ```
    time       phi      theta      psi     Unorth     Veast     Wdown    Xnorth     Yeast     Zdown      Vt       alpha     beta     Thrust     Lift      Drag itrim
     (s)      (deg)     (deg)     (deg)     (m/s)     (m/s)     (m/s)      (m)       (m)       (m)      (m/s)     (deg)     (deg)      (N)       (N)       (N)
    0.001     0.000    -0.000     0.000    -0.000    -0.000     0.010    -0.000    -0.000     0.000     0.010    90.000    -0.000     0.001     0.000     0.000  13
    1.000  -129.425   -28.251    43.780     1.071    -0.336     8.872     0.689    -0.334     4.421     8.943   -49.937   -35.667    29.468     0.000     1.511  13
    2.000  -161.604    -4.816    51.111     1.091    -0.071    16.420     1.770    -0.525    17.249    16.457   -82.745   -15.141    33.383     0.000     6.148  13
    3.000   128.637    41.555    31.242     1.144     0.368    22.199     2.890    -0.381    36.697    22.231  -142.470    38.225    35.160     0.000    16.664  13
    4.000    26.315    31.183   -35.818     1.222     0.786    26.341     4.071     0.140    61.067    26.381   123.595    25.420    36.618     0.000    15.175  13
    5.000   -36.710   -12.203   -41.762     1.315     0.994    29.200     5.336     0.946    88.963    29.247    74.757   -32.522    37.972     0.000     5.877  13
    6.000   -43.829   -12.248   -47.812     1.415     1.099    31.004     6.690     1.906   119.219    31.056    73.786   -39.306    40.902     0.000     6.974  13
    7.000  -138.688    -4.605     1.888     1.548     1.122    31.893     8.156     2.956   150.788    31.950   -79.830   -42.795    32.314     0.000    11.920  13
    8.000  -135.951     0.176    -7.853     1.918     1.234    32.095     9.878     4.103   182.882    32.176   -85.763   -46.618    35.402     0.000    12.812  13
    ```
    """

    @generate
    def header_str_parser():

        header_cols = {
            'time': 'time',
            'phi': 'phi',
            'theta': 'theta',
            'psi': 'psi',
            'Unorth': 'u_north',
            'Veast': 'v_east',
            'Wdown': 'w_down',
            'Xnorth': 'x_north',
            'Yeast': 'y_east',
            'Zdown': 'z_down',
            'Vt': 'v_t',
            'alpha': 'alpha',
            'beta': 'beta',
            'Thrust': 'thrust',
            'Lift': 'lift',
            'Drag': 'drag',
            'itrim': 'trim_state',
        }

        col_parsers = [string(k).result(v) for k, v in header_cols.items()]

        cols = yield alt(*col_parsers).sep_by(whitespace)

        return cols

    header_line_parser = parse_strip_line(header_str_parser)

    @generate
    def units_str_parser():

        units = yield in_parens.sep_by(whitespace)

        return [u if u != '-' else None for u in units]

    units_line_parser = parse_strip_line(units_str_parser)

    def row_line_parser(base_cols, base_units):
        """
        Parses lines like:
        ```
        0.001     0.000    -0.000     0.000    -0.000    -0.000     0.010    -0.000    -0.000     0.000     0.010    90.000    -0.000     0.001     0.000     0.000  13
        ```
        """

        @generate
        def row_str_parser():

            row = dict()

            num_base = len(base_cols)
            values = yield scientific.sep_by(whitespace, min=num_base, max=num_base)
            for (i, val) in enumerate(values):
                unit = None
                if i < len(base_units) and base_units[i]:
                    unit = base_units[i]

                row[base_cols[i]] = with_units(val, unit)

            return row

        return parse_strip_line(row_str_parser)

    cols = yield header_line_parser
    units = yield units_line_parser
    rows = yield row_line_parser(cols,units).at_least(1)

    return {'run_states': rows}

hackathon_state_table_block_parser = parse_block('hackathon_state_table', state_table_lines_parser)

@generate
def calc_complete_str_parser():
    """
    Parses lines like:
    ```
    Calculation completed at time    8.62500000      due to an electrical issue.
    ```
    """

    known_causes = {
        'an electrical issue' : 'electrical_failure',
        'course completion' : 'course_completion',
        'set time_end': 'timeout',
    }

    known_cause_parser = alt(
        *[string(k).result(v) for k,v in known_causes.items()]
    )

    unknown_cause_parser = not_char('.').at_least(1).concat().map(to_undercase)

    stop_info = yield format_parser(
        "Calculation completed at time   ${stop_time}$s?"\
        "due to ${stop_reason}.",
        stop_time=scientific,
        stop_reason=alt(known_cause_parser, unknown_cause_parser)
    )

    return stop_info

calc_complete_line_parser = parse_strip_line(calc_complete_str_parser)

no_flight_path_defined_line_parser = parse_strip_line(
    format_parser(
        'No flight path defined for path = ${undefined_flight_path}',
        undefined_flight_path=int_p,
    )
)


performance_header_line_parser = parse_strip_line(
    string("The following information is about electrical performance.")
)

electrical_disabled_line_parser = parse_strip_line(
    string("Flight termination due to electrical issues was turned off.")
)

@generate
def battery_info_str_parser():
    """
    Parses lines like:
    ```
    Battery  1  fraction capacity used     0.0365 and fraction max continuous amperage used     0.2750
    ```
    """

    info = yield format_parser(
        "Battery  ${number}  "\
        "fraction capacity used     ${capacity_used} "\
        "and fraction max continuous amperage used     ${current_used}",
        number = int_p,
        capacity_used = scientific,
        current_used = scientific,
    )

    return {
        info['number'] : {
            'capacity_used' : info['capacity_used'],
            'current_used' : info['current_used'],
        },
    }

battery_info_line_parser = parse_strip_line(battery_info_str_parser)

@generate
def motor_info_str_parser():
    """
    Parses lines like:
    ```
    Motor  1 fraction max amps reached     1.0000 and fraction max power reached     1.0006
    ```
    """

    info = yield format_parser(
        "Motor  ${number} "\
        "fraction max amps reached     ${current_used} "\
        "and fraction max power reached     ${power_used}",
        number = digits.map(int),
        current_used = scientific,
        power_used = scientific,
    )

    return {
        info['number'] : {
            'power_used' : info['power_used'],
            'current_used' : info['current_used'],
        },
    }

motor_info_line_parser = parse_strip_line(motor_info_str_parser)

@generate
def electrical_performance_lines_parser():

    output = dict()

    yield performance_header_line_parser
    output |= yield electrical_disabled_line_parser.exists('ignoring_electrical_issues')
    output |= yield battery_info_line_parser.union_many().dtag('battery_performance')
    output |= yield motor_info_line_parser.union_many().dtag('motor_performance')

    return output

hackathon_electrical_performance_block_parser = parse_block(
    'hackathon_electrical_performance', electrical_performance_lines_parser
)


@generate
def max_distance_error_str_parser():
    """
    Parses lines like:
    ```
    Maximum distance error (measured perpendicularly) from flight path was    665.766785      m
    ```
    """

    result = yield format_parser(
        "Maximum distance error (measured perpendicularly) from flight "\
        "path was    ${value}      ${units}",
        units=not_space.at_least(1).concat(),
        value=scientific,
    )

    return {'max_distance_error': result}

max_distance_error_line_parser = parse_strip_line(max_distance_error_str_parser)


units_info_line_parser = parse_strip_line(
    format_parser(
        'Measures of flight path performance '\
        '(distance in meters, time is seconds, speed in '\
        'meters per second)'
    ).result({})
)

path_traverse_success_line_parser = parse_strip_line(
    format_parser(
        'Flight path was successfully traversed.'
    ).result({})
)

path_traverse_failure_line_parser = parse_strip_line(
    format_parser(
        'Flight path was not successfully traversed.'
    ).result({})
)

path_traverse_line_parser = tag_alt(
    'path_traversed',
    true=path_traverse_success_line_parser,
    false=path_traverse_failure_line_parser,
)

hackathon_misc_line_parsers = [
    calc_complete_line_parser,
    no_flight_path_defined_line_parser,
    max_distance_error_line_parser,
    units_info_line_parser,
    path_traverse_line_parser,
]

hackathon_misc_line_parser = alt(*hackathon_misc_line_parsers)

hackathon_misc_block_parser = parse_block(
    'hackathon_misc', hackathon_misc_line_parser.at_least(1)
)

hackathon_component_lines_parsers = [
    hackathon_misc_line_parser,
    misc_vars_line_parser,
    state_table_lines_parser,
    electrical_performance_lines_parser,
    path_score_lines_parser,
]

@generate
def hackathon_lines_parser():
    output = dict()

    output |= yield hackathon_open_lines_parser << blank_line.many()
    components = yield alt(
        *hackathon_component_lines_parsers
    ).sep_by(blank_line.many())

    return output | unions(components)

hackathon_block_parser = parse_block('hackathon', hackathon_lines_parser)


"""
  Hackathon            1
  Path performance, flight path            3
  Downward force (N) = mg =    20.7864780

     time       phi      theta      psi     Unorth     Veast     Wdown    Xnorth     Yeast     Zdown      Vt       alpha     beta     Thrust     Lift      Drag itrim
      (s)      (deg)     (deg)     (deg)     (m/s)     (m/s)     (m/s)      (m)       (m)       (m)      (m/s)     (deg)     (deg)      (N)       (N)       (N)
     0.001     0.000    -0.000     0.000    -0.000    -0.000     0.010    -0.000    -0.000     0.000     0.010    90.000    -0.000     0.001     0.000     0.000  13
     1.000  -129.425   -28.251    43.780     1.071    -0.336     8.872     0.689    -0.334     4.421     8.943   -49.937   -35.667    29.468     0.000     1.511  13
     2.000  -161.604    -4.816    51.111     1.091    -0.071    16.420     1.770    -0.525    17.249    16.457   -82.745   -15.141    33.383     0.000     6.148  13
     3.000   128.637    41.555    31.242     1.144     0.368    22.199     2.890    -0.381    36.697    22.231  -142.470    38.225    35.160     0.000    16.664  13
     4.000    26.315    31.183   -35.818     1.222     0.786    26.341     4.071     0.140    61.067    26.381   123.595    25.420    36.618     0.000    15.175  13
     5.000   -36.710   -12.203   -41.762     1.315     0.994    29.200     5.336     0.946    88.963    29.247    74.757   -32.522    37.972     0.000     5.877  13
     6.000   -43.829   -12.248   -47.812     1.415     1.099    31.004     6.690     1.906   119.219    31.056    73.786   -39.306    40.902     0.000     6.974  13
     7.000  -138.688    -4.605     1.888     1.548     1.122    31.893     8.156     2.956   150.788    31.950   -79.830   -42.795    32.314     0.000    11.920  13
     8.000  -135.951     0.176    -7.853     1.918     1.234    32.095     9.878     4.103   182.882    32.176   -85.763   -46.618    35.402     0.000    12.812  13

  Calculation completed at time    8.62500000      due to an electrical issue.

  The following information is about electrical performance.
   Battery  1  fraction capacity used     0.0365 and fraction max continuous amperage used     0.2750
   Motor  1 fraction max amps reached     1.0000 and fraction max power reached     1.0006
   Motor  2 fraction max amps reached     1.0000 and fraction max power reached     1.0012
   Motor  3 fraction max amps reached     1.0000 and fraction max power reached     1.0010
   Motor  4 fraction max amps reached     1.0000 and fraction max power reached     1.0006

  Wind speed (m/s)    0.00000000       0.00000000       0.00000000
  Air density (kg/m^3)    1.22500002

  Hackathon            1
  Path performance, flight path            3

  Maximum distance error (measured perpendicularly) from flight path was    665.766785      m
  Score is zero since full circle not flown
  Final score (rounded) =    0.00000000

  Measures of flight path performance (distance in meters, time is seconds, speed in meters per second)

  Flight path was not successfully traversed.
  """
