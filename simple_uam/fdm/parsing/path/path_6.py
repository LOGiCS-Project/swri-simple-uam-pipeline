from parsy import *
from copy import deepcopy, copy
from ..line_parser import *
from ..block_parser import *
from ..util import *
from simple_uam.util.logging import get_logger
log = get_logger(__name__)

score_open_line_parser = parse_strip_line(
    format_parser(
        'Acceleration test path where input initial '\
        'speed, final speed, and requested '\
        'acceleration or deceleration determine '\
        'distance and time.'
    )
)

req_init_speed_line_parser = parse_strip_line(
    format_parser(
        'Requested initial speed (from '\
        'start_trim_state): ${requested_initial_speed}',
        requested_initial_speed=scientific.with_units('m/s'),
    )
)

final_speed_line_parser = parse_strip_line(
    format_parser(
        'Requested final speed (from '\
        'requested_lateral_speed): ${requested_final_speed} '\
        'Actual final speed = ${actual_final_speed}',
        requested_final_speed=scientific.with_units('m/s'),
        actual_final_speed=scientific.with_units('m/s'),
    )
)

requested_acceleration_line_parser = parse_strip_line(
    format_parser(
        'Requested acceleration (+) or deceleration '\
        '(-): ${requested_acceleration}',
        requested_acceleration=scientific.with_units('m/s^2'),
    )
)

distance_line_parser = parse_strip_line(
    format_parser(
        'Expected distance: ${expected_distance} '\
        'Distance flown = ${actual_distance}',
        expected_distance=scientific.with_units('m'),
        actual_distance=scientific.with_units('m'),
    )
)

time_line_parser = parse_strip_line(
    format_parser(
        '    Expected time: ${expected_time}'\
        '  Actual time = ${actual_time}',
        expected_time=scientific.with_units('s'),
        actual_time=scientific.with_units('s'),
    )
)

score_line_parser = parse_strip_line(
    format_parser(
        '    This is not a scored path, but a score of'
        ' path distance/10  - 10 * error >= 0'
        ' is provided for analysis: ${base_score}',
        base_score=digits.map(int),
    )
)

@generate
def path_6_score_line_parser():

    result = dict()

    yield score_open_line_parser << blank_line.many()
    result |= yield req_init_speed_line_parser << blank_line.many()
    result |= yield final_speed_line_parser << blank_line.many()
    result |= yield requested_acceleration_line_parser << blank_line.many()
    result |= yield distance_line_parser << blank_line.many()
    result |= yield time_line_parser << blank_line.many()
    result |= yield score_line_parser

    return {
        'scored_path': 6,
        'path_type': 'straight_line_flight',
        **result
    }

path_6_score_block_parser = parse_block('path_6_score', path_6_score_line_parser)
