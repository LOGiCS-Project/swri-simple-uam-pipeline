from parsy import *
from .line_parser import *
from .block_parser import *
from .util import *
from .motor_power_block import motor_power_block
from .state_desc_block import state_desc_block, control_desc_block
from .minpack_trim_block import minpack_trim_block
from .metrics_block import metrics_block
from simple_uam.util.logging import get_logger
from attrs import define, field
log = get_logger(__name__)

# These are the blocks that can appear in the fdm dump file, in order of what
# priority we should detect them in.
fdm_dump_blocks = [
    # metrics_block,
    # state_desc_block,
    minpack_trim_block,
    # control_desc_block,
    # motor_power_block,
    blank_block,
    # raw_line_block,
    ]

def parse_fdm_dump(string):
    """
    Parses a path input string, outputs

    Returns:
      output: list of dicts of each row of data in the file
    """

    fdm_blocks_parser = alt(
        *[p for p in fdm_dump_blocks]
    ).at_least(1)

    input = string.splitlines()

    try:
        blocks = run_blockparser(fdm_blocks_parser, input)
        groups = group_blocks(blocks)
        return collapse_groups(
            groups,
            raw_line=collapse_raw_line_group,
            blank_block=lambda x: None,
        )
    except Exception as err:
        log.exception("error while parsing fdm file")
        raise err
