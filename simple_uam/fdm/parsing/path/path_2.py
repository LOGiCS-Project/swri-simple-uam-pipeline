from parsy import *
from copy import deepcopy, copy
from ..line_parser import *
from ..block_parser import *
from ..util import *
from simple_uam.util.logging import get_logger
log = get_logger(__name__)


base_score_line_parser = parse_strip_line(
    format_parser(
        "Score is distance flown / 10 = ${base_score} "\
        "since minimum flight distance of 2 km achieved",
        base_score=scientific,
    )
)

capped_score_line_parser = parse_strip_line(
    format_parser(
        "The maximum score on flight distance is 400 "\
        "so score is = ${capped_score}",
        capped_score=scientific,
    )
)

distance_error_line_parser = parse_strip_line(
    format_parser(
        "Score is now deducted for inaccuracy "\
        "by 10 * distance error ${distance_error_penalty}",
        distance_error_penalty=scientific,
    )
)

@generate
def path_2_success_line_parser():

    output = dict()

    output |= yield base_score_line_parser

    yield black_line.many()

    output |= yield capped_score_line_parser.optional({})

    yield black_line.many()

    output |= yield distance_error_line_parser.optional({})

    return output

path_distance_line_parser = parse_strip_line(
    format_parser(
        "Score is 0 since minimum flight distance "\
        "of 2 km not achieved; distance was "\
        "${path_distance} m",
        path_distance=scientific.with_units('m'),
    )
)

@generate
def path_2_score_line_parser():
    result = yield tag_alt(
        'path_complete',
        true=path_2_success_line_parser,
        false=path_distance_line_parser,
    )

    return {
        'scored_path': 2,
        'path_type': 'straight_line_flight',
        **result
    }

path_2_score_block_parser = parse_block('path_2_score', path_2_score_line_parser)
