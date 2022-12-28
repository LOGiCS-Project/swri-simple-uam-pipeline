from parsy import *
from .line_parser import *
from copy import deepcopy, copy
from simple_uam.util.logging import get_logger
from typing import Optional, List
log = get_logger(__name__)
from attrs import define, field
import attrs

@define(hash=True)
class ExpectedBlock():
    block_type : str = field()
    start_line : int = field()
    expected = field()

@define
class BlockVal():
    """
    The output data for a single parsed block.
    """

    type : str = field()
    start_line : int = field()
    end_line : int = field()
    data = field()

@define
class BlockGroup():
    """
    A group of blocks of identical type.
    """

    type : Optional[str] = field(default = None)
    members : List[BlockVal] = field(factory= list)

    def add(self, block):
        """
        Adds a block value to this group.
        """

        if self.type == None:
            self.type = block.type

        if block.type != self.type:
            raise RuntimeError(
                f"Cannot add block of type '{block.type}' "\
                f"to group of type '{self.type}'."
            )

        self.members.append(block)

    @property
    def start_line(self):
        return min([b.start_line for b in self.members])

    @property
    def end_line(self):
        return max([b.end_line for b in self.members])

def parse_block(block_type, line_parser):
    """
    Converts a parser over lines into a parser for a single, typed block of
    data.
    """

    @Parser
    def run_block(lines, start_line):

        if start_line >= len(lines):
            return Result.failure(start_line, f'No more lines in input.')

        # log.debug(
        #     "Parsing block at",
        #     block_type = block_type,
        #     start_line = start_line,
        #     line = lines[start_line],
        # )

        result = line_parser(lines, start_line)
        if result.status:

            # log.debug(
            #     "Successfully parsed block at",
            #     block_type = block_type,
            #     start_line = start_line,
            #     line = lines[start_line],
            #     val=result.value,
            # )

            block_value = BlockVal(
                type = block_type,
                start_line = start_line,
                end_line = result.index,
                data = deepcopy(result.value),
                # raw_lines = deepcopy(lines[start_line:next_line]),
            )

            return Result.success(result.index, block_value)

        else:

            exp = ExpectedBlock(
                start_line = start_line,
                block_type= block_type,
                expected = result.expected,
            )

            return Result.failure(result.furthest, exp)

    return run_block


# Parses a single blank line.
blank_block = parse_block('blank_block', blank_line)

# Parses any one line of input.
raw_line_block = parse_block('raw_line', raw_line)

def wrap_blankblocks(block_parser):
    """
    Wrap a block_parser so that it will eat blank space around it.
    """

    @generate
    def wrapped():
        yield blank_block.many()
        res = yield block_parser
        yield blank_block.many()
        return res

    return wrapped

def run_blockparser(parser, string):
    """
    Splits an input string into lines and then runs a block parser over them.
    """

    if isinstance(string, str):
        lines = string.splitlines()
    else:
        lines = string

    return parser.parse(lines)

# Stuff for working with groups of blocks.

def group_blocks(block_list):
    """
    Goes through a list of blocks and groups them by block type, keeping
    track of each groups start and end location.
    """

    any_block = test_item(lambda _: True, "Any single block")
    block_of = lambda b_type: test_item(lambda b: b.type == b_type, f"block of type {b_type}")

    @generate
    def run_of_blocks():
        """
        Parses a run of identically typed blocks from a list.
        """

        init = yield any_block
        rest = yield block_of(init.type).many()

        return BlockGroup(init.type, [init] + rest)

    return run_of_blocks.many().parse(block_list)

def collapse_groups(group_list, rules, default=None):
    """
    Will collapse a list of blockgroups into a list of blocks using the rules
    given by the user.

    Arguments:
      group_list: The list of groups we're going to collapse
      rules: a dict whose keys are block types and whose functions turn a
        BlockGroup into a list of BlockVals. If None instead of a function then
        all groups of that type will be ignored.
      default: the rule to apply for all block types not found in the rules
        dictionary. (Default: Use the members from the group)
    """

    def run_rule(group):

        rule = lambda g: g.members

        if group.type in rules and rules[group.type] == None:
            rule = lambda g: []
        elif group.type in rules:
            rule = rules[group.type]
        elif default != None:
            rule = default

        return rule(group)

    return [blk for grp in group_list for blk in run_rule(grp)]

def concat_raw(raw_group):
    """
    A rule for use with collapse_groups, will concatenate raw lines into a
    larger raw_lines block.
    """

    if raw_group.type != 'raw_line':
        raise RuntimeError("can only use concat_raw with 'raw_line' groups.")

    return [BlockVal(
        type='raw_lines',
        start_line=raw_group.start_line,
        end_line=raw_group.end_line,
        data=[blk.data for blk in raw_group.members],
    )]
