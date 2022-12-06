from parsy import *
from .line_parser import *
from copy import deepcopy, copy
from simple_uam.util.logging import get_logger
log = get_logger(__name__)

def parse_block(block_type, line_parser):
    """
    Converts a parser over lines into a parser for a single, typed block of
    data.
    """

    @Parser
    def run_block(lines, start_line):

        if start_line >= len(lines):
            return Result.failure(start_line, f'No more lines in input.')


        #print(start_line)
        log.debug(
            "Parsing block at",
            block_type = block_type,
            start_line = start_line,
            line = lines[start_line],
        )

        result = line_parser(lines, start_line)
        if result.status:

            block_value = {
                'type': block_type,
                'start_line': start_line,
                'end_line': result.index,
                'data': deepcopy(result.value),
                # 'raw_lines': deepcopy(lines[start_line:next_line]),
            }

            return Result.success(result.index, block_value)

        else:

            return Result.failure(result.furthest, result.expected)


        # remaining_len = len(remainder)
        # parsed_len = unparsed_len - remaining_len
        # next_line = start_line + parsed_len
        # end_line = next_line - 1

        # eturn Result.success(next_line, output)
        # pt ParseError as err:
        # return Result.failure(start_line, str({
        #     'type': block_type,
        #     'start_line': start_line,
        #     'error': err,
        # }))

    return run_block

def block_is(block_type, desc=""):
    """
    A simple primitive used for parsing only blocks with a given block_type.
    """

    return test_item(lambda b: 'type' in b and b['type'] == block_type, desc)

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

def group_blocks(block_list):
    """
    Goes through a list of blocks and groups them by block type, keeping
    track of each groups start and end location.
    """

    groups = list()

    current_type = None
    current_start = None
    current_end = None
    current_members = None

    for block in block_list:

        # Start new group because current block has new type.
        if block['type'] != current_type:

            # Finalize and push old group
            if current_members != None:
                groups.append({
                    'type': current_type,
                    'start_line': current_start,
                    'end_line': current_end,
                    'members': current_members,
                })

            # Reset current group
            current_type = block['type']
            current_start = block['start_line']
            current_end = block['end_line']
            current_members = list()

        # Add the current block to the group
        current_end = block['end_line']
        current_members.append(block)

    # Finalize and push the last group
    if current_members != None:
        groups.append({
            'type': current_type,
            'start_line': current_start,
            'end_line': current_end,
            'members': current_members,
        })

    return groups

def collapse_groups(groups, **collapse_funcs):
    """
    Will run through a list of groups and collapse them using a function in
    the collapse_funcs dict.
    """

    output = list()

    for group in groups:
        group_type = group['type']
        if group_type in collapse_funcs:
            collapsed = collapse_funcs[group_type](group)
            if collapsed != None:
                output.append(collapsed)
        else:
            output += group['members']

    return output

def collapse_raw_line_group(group):
    """
    collapses a bunch of raw line blocks into a raw_lines block.
    """
    return {
        'type': 'raw_lines',
        'start_line': group['start_line'],
        'end_line': group['end_line'],
        'data': [b['data'] for b in group['members']],
    }


def run_blockparser(parser, string):
    """
    Splits an input string into lines and then runs a block parser over them.
    """

    if isinstance(string, str):
        lines = string.splitlines()
    else:
        lines = string

    return parser.parse(lines)
