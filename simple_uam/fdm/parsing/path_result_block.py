
from parsy import *
from .line_parser import *
from .block_parser import *
from .util import *
from .misc_vars_block import *
from .path.path_1 import path_1_score_block_parser, path_1_score_line_parser
from .path.path_2 import path_2_score_block_parser, path_2_score_line_parser
from .path.path_3 import path_3_score_block_parser, path_3_score_line_parser
from .path.path_4 import path_4_score_block_parser, path_4_score_line_parser
from .path.path_5 import path_5_score_block_parser, path_5_score_line_parser
from .path.path_6 import path_6_score_block_parser, path_6_score_line_parser
from .path.path_7plus import path_7plus_score_block_parser, path_7plus_score_line_parser
from simple_uam.util.logging import get_logger
from attrs import define, field
log = get_logger(__name__)

all_path_score_block_parsers = [
    path_1_score_block_parser,
    path_2_score_block_parser,
    path_3_score_block_parser,
    path_4_score_block_parser,
    path_5_score_block_parser,
    path_6_score_block_parser,
    path_7plus_score_block_parser,
]

all_path_score_line_parsers = [
    path_1_score_line_parser,
    path_2_score_line_parser,
    path_3_score_line_parser,
    path_4_score_line_parser,
    path_5_score_line_parser,
    path_6_score_line_parser,
    path_7plus_score_line_parser,
]


electrical_cheat_score_line_parser = parse_strip_line(
    format_parser(
        'Score ignoring electrical issues ${cheat_score}',
        cheat_score=scientific,
    )
)
electrical_cheat_reset_line_parser = parse_strip_line(
    format_parser(
	    'However, score set to 0 because of electrical issue.'
    )
)

electrical_cheat_lines_parser = (
    electrical_cheat_score_line_parser << electrical_cheat_reset_line_parser
)

wingload_cheat_score_line_parser = parse_strip_line(
    format_parser(
        'Score ignoring wing loading$s?${cheat_score}',
        cheat_score=scientific,
    )
)
wingload_cheat_reset_line_parser = parse_strip_line(
    format_parser(
        'However, score set to 0 because of wing loading '\
        'check was turned off.'
    )
)

wingload_cheat_lines_parser = (
    wingload_cheat_score_line_parser << wingload_cheat_reset_line_parser
)

@generate
def cheat_score_lines_parser():

    output = {
        'ignoring_electrical': False,
        'ignoring_wingload':True,
    }

    # We do this awkwardly in order to ensure the parser doesn't consume
    # input on an empty string.
    temp = yield tag_alt(
        'term', 'data',
        elec=electrical_cheat_lines_parser,
        wing=wingload_cheat_lines_parser,
    )

    if temp['term'] == 'wing':
        # no electrical just return data w/ flag
        output |= {'ignoring_wingload':True, **temp['data']}
    else:
        # Electrical will appear before wingload, but the 'cheat_score' from
        # electrical should take precedence.
        output |= yield wingload_cheat_lines_parser.exists('ignoring_wingload')
        output |= {'ignoring_electrical':True, **temp['data']}

    return output

cheat_score_block_parser = parse_block('cheat_score', cheat_score_lines_parser)

final_score_line_parser = parse_strip_line(
    format_parser(
        'Final score (rounded) = ${final_score}',
        final_score=scientific,
    )
)

final_score_block_parser = parse_block('final_score', final_score_line_parser)

@generate
def path_score_lines_parser():

    output = dict()
    output |= yield alt(*all_path_score_line_parsers) << blank_line.many()
    output |= yield cheat_score_lines_parser.optional({}) << blank_line.many()
    output |= yield final_score_line_parser

    return output

path_score_block_parser = parse_block('path_score', path_score_lines_parser)
