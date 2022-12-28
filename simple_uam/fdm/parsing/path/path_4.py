from parsy import *
from copy import deepcopy, copy
from ..line_parser import *
from ..block_parser import *
from ..util import *
from simple_uam.util.logging import get_logger
log = get_logger(__name__)

score_open_line_parser = parse_strip_line(
    format_parser(
        'Since minimum flight time of 200 s '\
        'was achieved and final vehicle height was '\
        'within 2 m of specified hover height, '\
        'score is flight time with max 400 pts.'
    )
)

height_time_line_parser = parse_strip_line(
    format_parser(
        'Final height (-Z) = '\
        '${final_height}$s?m;  '\
        'flight time = ${flight_time}$s?s',
        final_height = scientific.with_units('m'),
        flight_time = scientific.with_units('s'),
    )
)


@generate
def path_4_success_line_parser():

    output = dict()

    yield score_open_line_parser
    yield black_line.many()
    output |= yield height_time_line_parser

    return output

bad_height_line_parser = parse_strip_line(
    format_parser(
        'Score is zero since final hover not '\
        'within 2 m of specified height; height -Z = '\
        '${final_height}$s?m',
        final_height=scientific.with_units('m'),
    )
)

bad_time_line_parser = parse_strip_line(
    format_parser(
        'Score is zero since flight time less '\
        'than 200 s; flight time = ${flight_time}$s?s',
        flight_time=scientific.with_units('s'),
    )
)

path_4_failure_line_parser = tag_alt(
    'failure_cause',
    incorrect_hover_height=bad_height_line_parser,
    insufficient_flight_time=bad_time_line_parser,
)

@generate
def path_4_score_line_parser():

    result = yield tag_alt(
        'path_complete',
        true=path_4_success_line_parser,
        false=path_4_failure_line_parser,
    )

    return {
        'scored_path': 4,
        'path_type': 'vertical_rise',
        **result
    }

path_4_score_block_parser = parse_block('path_4_score', path_4_score_line_parser)
