from parsy import *
from copy import deepcopy, copy
from .line_parser import *
from .block_parser import *
from .util import *
from simple_uam.util.logging import get_logger
log = get_logger(__name__)

all_static_lines = list()

def new_static_block(string, file=None, line=None):
    # nonlocal all_static_lines
    parser = static_lines(string)
    all_static_lines.append(parser)
    return parser

opening_line = new_static_block(
    "This is the output file for the SwRI flight dynamics model.",
    file='new_fdm.f',
    line=54,
)

power_disclaimer = new_static_block(
    """
    Information on propeller/motor performance assumes the vehicle is at rest.  In this list, the power and current are the
    power and current supplied by the battery.  To obtain the current and power in the motor, it is necessary to reduce the
    values by multiplying by efficiency_ESC.  The Efficiency is the motor efficiency - i.e., there is no knockdown for the ESC.
    When the three different approaches yield similar values for the motor/propeller/battery, then they are appropriately sized.
    Otherwise, there is mass inefficiency.

    The Max Volt entry uses the battery voltage and the motor and propeller properties.  If the resulting power and current are less
    than the motor rated values then a larger voltage battery or a larger propeller or a smaller motor is suggested.

    The Max Power and Max Amps use the power and current rating from the motor, respectively, and the motor and propeller properties
    (no battery properties are used).  An appropriate battery voltage for the motor can be estimated by motor max power/max current.
    """,
    file='new_fdm.f',
    line=658,
)

frame_key = new_static_block(
    """
    The body  frame is frd: x forward, y right, z down (down is positive)
    The world frame is ned: X north,   Y east,  Z down (down is positive, so altitude (up) is negative)
    """,
    file='new_fdm.f',
    line=89,
)

static_blocks= parse_block("static_text", alt(*all_static_lines))
