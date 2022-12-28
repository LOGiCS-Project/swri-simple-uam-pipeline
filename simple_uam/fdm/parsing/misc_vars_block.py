from parsy import *
from copy import deepcopy, copy
from .line_parser import *
from .block_parser import *
from .util import *
from simple_uam.util.logging import get_logger
log = get_logger(__name__)

@generate
def downward_force_str_parser():
    """
    Parses lines like:
    ```
    Downward force (N) = mg =    20.7864780
    ```
    """

    result = yield format_parser(
        "Downward force ${units} = mg =    ${value}",
        units=in_parens,
        value=scientific,
    )

    return {'downward_force': result}

downward_force_line_parser = parse_strip_line(downward_force_str_parser)

@generate
def wind_speed_str_parser():
    """
    Parses lines like:
    ```
    Wind speed (m/s)    0.00000000       0.00000000       0.00000000
    ```
    """

    result = yield format_parser(
        "Wind speed ${units}    ${u}       ${v}       ${w}",
        units= in_parens,
        u=scientific,
        v=scientific,
        w=scientific,
    )

    return {'wind_speed': result}

wind_speed_line_parser = parse_strip_line(wind_speed_str_parser)

@generate
def air_density_str_parser():
    """
    Parses lines like:
    ```
    Air density (kg/m^3)    1.22500002
    ```
    """

    result = yield format_parser(
        "Air density ${units}    ${value}",
        units= in_parens,
        value=scientific,
    )

    return {'air_density': result}

air_density_line_parser = parse_strip_line(air_density_str_parser)

all_misc_vars_parsers = [
    downward_force_line_parser,
    wind_speed_line_parser,
    air_density_line_parser,
    # aircraft_simplex_line_parser,
]

misc_vars_line_parser = alt(*all_misc_vars_parsers)

misc_vars_block = parse_block('misc_vars', misc_vars_line_parser.at_least(1))
