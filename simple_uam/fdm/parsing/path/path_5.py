from parsy import *
from copy import deepcopy, copy
from ..line_parser import *
from ..block_parser import *
from ..util import *
from simple_uam.util.logging import get_logger
log = get_logger(__name__)

score_open_line_parser = parse_strip_line(
    format_parser(
        'Complete oval being flown gives 200 pts.'
    )
)

flight_time_line_parser = parse_strip_line(
    format_parser(
        'Every second less than 350 seconds gives '\
        'one additional point; flight time = ${flight_time}',
        flight_time=scientific.with_units('s'),
    )
)

score_close_line_parser = parse_strip_line(
    format_parser(
        'Stayed with 10 m of flight path (otherwise '\
        'no points would have been awarded)'
    )
)

@generate
def path_5_success_line_parser():

    output = dict()

    yield score_open_line_parser
    yield black_line.many()
    output |= yield flight_time_line_parser
    yield black_line.many()
    yield score_close_line_parser

    return output

incomplete_flight_line_parser = parse_strip_line(
    format_parser(
        'Zero points since complete oval not flown'
    )
)

distance_error_line_parser = parse_strip_line(
    format_parser(
        'Since distance error from specified flight '\
        'path exceeds 10 m, 0 points are awarded'
    )
)

distance_success_line_parser = parse_strip_line(
    format_parser(
        'Stayed with 10 m of flight path (otherwise '\
        'no points would have been awarded)'
    )
)

@generate
def path_5_score_line_parser():

    complete = yield tag_alt(
        'is', 'data',
        true=path_5_success_line_parser,
        false=incomplete_flight_line_parser,
    )

    accurate = yield tag_alt(
        'is', 'data',
        true=distance_success_line_parser,
        false=distance_error_line_parser,
    )

    result = dict()

    result['path_complete'] = complete['is'] and accurate['is']

    if result['path_complete']:
        result |= complete['data']
    elif not complete['is'] and not accurate['is']:
        result['failure_cause'] = 'incomplete_oval_and_distance_error_exceeded'
    elif not complete['is']:
        result['failure_cause'] = 'incomplete_oval'
    elif not accurate['is']:
        result['failure_cause'] = 'distance_error_exceeded'

    return {
        'scored_path': 5,
        'path_type': 'racing_oval',
        **result
    }

path_5_score_block_parser = parse_block('path_5_score', path_5_score_line_parser)
