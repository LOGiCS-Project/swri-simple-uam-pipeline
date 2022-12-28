from parsy import *
from .line_parser import *
from .block_parser import *
from .util import *
from .metrics_block import metrics_block
from .hackathon_block import \
    hackathon_open_block_parser, \
    hackathon_state_table_block_parser, \
    hackathon_electrical_performance_block_parser, \
    hackathon_misc_block_parser, \
    hackathon_block_parser
from .misc_vars_block import misc_vars_block
from .path_result_block import \
    path_score_block_parser, \
    final_score_block_parser, \
    cheat_score_block_parser
from .trim.general import \
    general_trim_block_parser, \
    general_trim_summary_block_parser, \
    general_trim_state_prefix_block_parser, \
    general_trim_prefix_block
from .trim.minpack import \
    minpack_trim_block_parser, \
    minpack_trim_summary_block_parser, \
    minpack_trim_state_block_parser, \
    minpack_trim_state_prefix_block_parser, \
    minpack_trim_prefix_block
from .trim.shared import \
    trim_state_vars_block_parser, \
    trim_state_battery_info_block_parser, \
    trim_state_controls_block_parser
from .state_desc_block import \
    state_desc_block, \
    control_desc_block, \
    parameters_block
from .motor_power_block import motor_power_block
from .static_blocks import static_blocks



from simple_uam.util.logging import get_logger
from attrs import define, field, asdict
import attr
from attr.exceptions import NotAnAttrsClassError
from pprint import pformat
import textwrap
log = get_logger(__name__)

# These are the blocks that can appear in the fdm dump file, in order of what
# priority we should detect them in.
fdm_dump_blocks = [
    metrics_block,
    hackathon_block_parser,
    minpack_trim_block_parser,
    general_trim_block_parser,
    parameters_block,
    motor_power_block,
    misc_vars_block,
    static_blocks,
    blank_block,
]

# These are blocks for the permissive parsing mode, that can be used when
# a slower, more robust parsing mode is called for.
#
# Note: These should be in reverse dependency order, so that a parser should
# appear in the list *before* any parsers it uses within itself.
fdm_permissive_blocks = [
    # Hackathon sub-block
    hackathon_misc_block_parser,
    hackathon_electrical_performance_block_parser,
    hackathon_state_table_block_parser,
    hackathon_open_block_parser,
    # Path result sub-blocks
    path_score_block_parser,
    final_score_block_parser,
    cheat_score_block_parser,
    # General trim sub-blocks
    general_trim_summary_block_parser,
    general_trim_state_prefix_block_parser,
    general_trim_prefix_block,
    # Minpack trim sub-blocks
    minpack_trim_summary_block_parser,
    minpack_trim_state_block_parser,
    minpack_trim_state_prefix_block_parser,
    minpack_trim_prefix_block,
    # Shared trim sub-blocks
    trim_state_vars_block_parser,
    trim_state_battery_info_block_parser,
    trim_state_controls_block_parser,
    # Parameteriztion sub-blocks
    state_desc_block,
    control_desc_block,
]

# These are the catchall blocks that can appear in the FDM dump file, lines
# should only be matched to these blocks if all others fail.
fdm_catchall_blocks = [
    raw_line_block,
]

def clean_expected(inp):
    """
    Cleans up the expected values into something more pformat-able.
    """

    is_attrs = None
    try:
        is_attrs = attr.asdict(inp)
    except NotAnAttrsClassError as err:
        pass

    inp = is_attrs if is_attrs else inp

    if isinstance(inp, frozenset):

        inp = [clean_expected(i) for i in inp]

        if len(inp) == 1:
            inp = inp[0]

    elif isinstance(inp, dict):

        inp = {k: clean_expected(v) for k, v in inp.items()}

        inp = {k:v for k,v in inp.items() if v != None}

    return inp

def parse_fdm_dump(string, permissive=False, strict=False):
    """
    Parses an fdm dump formatted input string, outputs a json serializable
    object with nicely parsed data.

    Arguments:
      string: The input string
      permissive: If true will be more resilient to errors in the parser or
        the format of the file, at the cost of slower parsing and more types
        of output blocks (which only appear when trying to recover from an
        invalid parse).
      strict: If true will throw an error on unparsable input lines instead
        of collecting them in "raw_lines" blocks.
        Mostly useful for ensuring correctness of either the input or the
        parsers.

    Returns:
      output: list of parsed "blocks" from the input each with a fixed type
        (that determines the format of the data), start line, end line, and
        the data that was extracted.
    """

    fdm_blocks = list(fdm_dump_blocks)

    if permissive:
        fdm_blocks += fdm_permissive_blocks

    if not strict:
        fdm_blocks += fdm_catchall_blocks

    fdm_blocks_parser = alt(*fdm_blocks).at_least(1)

    input = string.splitlines()

    try:
        blocks = run_blockparser(fdm_blocks_parser, input)
        groups = group_blocks(blocks)

        collapsed = collapse_groups(
            groups,
            rules = {
                'raw_line': concat_raw,
                'blank_block': None,
                'static_text': None,
            },
            default = lambda g: g.members,
        )

        json_obj = force_string_keys(
            [attrs.asdict(blk) for blk in collapsed]
        )

        return json_obj

    except ParseError as err:
        log.error(
            textwrap.dedent(
                """
                Parse error while parsing fdm file.

                Expected Next Tokens:
                {}
                """
            ).format(pformat(clean_expected(err.expected), compact=True)),
            line_no= err.index,
            line = input[err.index],
        )
        # log.exception("error while parsing fdm file")
        raise err
