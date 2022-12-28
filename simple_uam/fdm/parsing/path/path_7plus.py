from parsy import *
from copy import deepcopy, copy
from ..line_parser import *
from ..block_parser import *
from ..util import *
from simple_uam.util.logging import get_logger
log = get_logger(__name__)

distance_error_line_parser = parse_strip_line(
    format_parser(
        'Maximum distance error '\
        '(measured perpendicularly) by Path$s?${scored_path} '\
        'scoring routine ${max_distance_error} m',
        scored_path = int_p,
        max_distance_error = scientific.with_units('m'),
    )
)

@generate
def flight_dist_str_parser():

    result = yield
    return {
        'scored_path': result['scored_path'],
        'flight_distance': {
            'value': result['fd_val'],
            'units': result['fd_units'],
        },
    }

flight_dist_line_parser = parse_strip_line(
    format_parser(
        'Path${scored_path} distance traveled within allowed '\
        'bounds: ${flight_distance} m',
        scored_path = int_p,
        flight_distance = scientific.with_units('m'),
    )
)

exit_time_line_parser = parse_strip_line(
    format_parser(
        'Exited allowable volume at time ${volume_exit_time}',
        volume_exit_time=scientific,
    )
)

base_score_line_parser = parse_strip_line(
    format_parser(
        'Base score based on distance traveled and '\
        'potential bonuses for transitions ${base_score}',
        base_score=scientific,
    )
)

distance_bullshit_line_parser = parse_strip_line(
    string('(Distance/10 + 200 + 200)')
)

path_complete_init_line_parser = parse_strip_line(
    format_parser(
        'Path${scored_path} completed, from take off to landing.',
        scored_path = int_p,
    )
)

ground_impact_speed_line_parser = parse_strip_line(
    format_parser(
        'Downward speed at landing was ${ground_impact_speed} m/s',
        ground_impact_speed=scientific.with_units('m/s'),
    )
)

crash_landing_line_parser = parse_strip_line(
    format_parser(
        'No bonus points owing to crash landing (greater than 0.2 m/s).'
    )
)

landing_bonus_line_parser = parse_strip_line(
    format_parser(
        'Bonus +1000 for completion and nice landing.'
    )
)

time_bonus_line_parser = parse_strip_line(
    format_parser(
        'Bonus ${time_bonus} for time less than 1000 seconds.',
        time_bonus=scientific,
    )
)

@generate
def good_landing_line_parser():

    yield landing_bonus_line_parser << blank_line.many()

    result = yield time_bonus_line_parser

    return result

@generate
def path_complete_line_parser():

    result = dict()

    result |= yield path_complete_init_line_parser << blank_line.many()

    result |= yield ground_impact_speed_line_parser << blank_line.many()

    result |= yield tag_alt(
        'crash_landing',
        true = crash_landing_line_parser.result({}),
        false = good_landing_line_parser
    )

    return result

path_incomplete_line_parser = parse_strip_line(
    format_parser(
        'Path${scored_path} not completed.',
        scored_path = int_p,
    )
)

@generate
def path_7plus_score_line_parser():


    result = dict()

    result |= yield distance_error_line_parser << blank_line.many()

    result |= yield flight_dist_line_parser << blank_line.many()

    result |= yield tag_alt(
        'exited_boundary_volume',
        true=exit_time_line_parser,
        false=success.result({}),
    ) << blank_line.many()


    result |= yield base_score_line_parser << blank_line.many()

    yield distance_bullshit_line_parser << blank_line.many()

    result |= yield tag_alt(
        'path_complete',
        true=path_complete_line_parser,
        false=path_incomplete_line_parser,
    )

    return {
        'path_type': 'unspecified',
        **result
    }

path_7plus_score_block_parser = parse_block(
    'path_7plus_score', path_7plus_score_line_parser)
