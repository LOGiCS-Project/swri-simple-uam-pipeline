from parsy import *
from copy import deepcopy, copy
from ..line_parser import *
from ..block_parser import *
from ..util import *
from simple_uam.util.logging import get_logger
log = get_logger(__name__)

base_score_line_parser = parse_strip_line(
    format_parser(
        "The full circle was flown, so 300 "\
        "points are initially awarded"
    ).result({'base_score': 300})
)

lateral_error_line_parser = parse_strip_line(
    format_parser(
        "Score is now deducted for inaccuracy "\
        "by 10 * maximum lateral error ${lateral_error_penalty}",
        lateral_error_penalty=scientific,
    )
)

@generate
def path_3_success_line_parser():

    output = dict()

    output |= yield base_score_line_parser

    yield black_line.many()

    output |= yield lateral_error_line_parser.optional({})

    return output

path_distance_line_parser = parse_strip_line(
    format_parser("Score is zero since full circle not flown")
)

@generate
def path_3_score_line_parser():

    result = yield tag_alt(
        'path_complete',
        true=path_3_success_line_parser,
        false=path_distance_line_parser.result({}),
    )

    return {
        'scored_path': 3,
        'path_type': 'circle',
        **result
    }

path_3_score_block_parser = parse_block('path_3_score', path_3_score_line_parser)
