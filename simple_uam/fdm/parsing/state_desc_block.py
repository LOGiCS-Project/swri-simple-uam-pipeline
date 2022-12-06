from parsy import *
from .line_parser import *
from .block_parser import *
from .util import *
from simple_uam.util.logging import get_logger
from attrs import define, field
log = get_logger(__name__)


def state_dimension_line():
    """
    This parses lines like:
    ```
    Number of state variables x: xdim =  18
    ```
    """

    @generate
    def str_parser():
        yield string("Number of state variables x: xdim =")
        yield whitespace.optional()
        xdim = yield digits
        return int(xdim)

    return parse_line(wrap_whitespace(str_parser))


def var_desc_line():
    """
    This parses lines like:
    ```
     x( 1 -  3) is velocity in body frame: U forward, V right, W down (m/s)
     x( 4 -  6) is angular velocity in body frame: P about x (roll rate), Q about y (pitch rate), R about z (yaw rate) (radians/s)
     x( 7 - 10) is quaternion connecting world frame to body frame: q0, q1, q2, q3
    ```
    """

    @generate
    def var_nums():
        """Parses: `x( 7 - 10)`"""

        yield seq(string('x('), whitespace.optional())
        lower = yield digits
        yield wrap_whitespace(string('-'))
        upper = yield digits
        yield seq(whitespace.optional(), string(')'))
        return (int(lower), int(upper) + 1)

    # text w/o some separators
    label = test_char(lambda c: c not in ":,()", "label").at_least(1).concat()

    @generate
    def label_w_note():
        """Parses: `P about x (roll rate)`"""

        text = yield label
        yield whitespace.optional()
        note = yield in_parens

        log.debug(
            "label w/ note",
            text=text,
            note=note,
        )
        return f"{text.strip()} ({note.strip()})"

    def sub_labels(count):

        sep = wrap_whitespace(string(','))
        no_note = label.sep_by(sep,min=count, max=count)
        w_note  = label_w_note.sep_by(sep, min=count, max=count)

        return (wrap_whitespace(string(':')) >> alt(w_note, no_note))

    @generate
    def desc_line():

        (lower, upper) = yield var_nums
        count = upper - lower
        yield wrap_whitespace(string('is'))
        grp_label = yield alt(label_w_note, label)
        yield whitespace.optional()
        var_labels = yield sub_labels(count).optional()
        yield whitespace.optional()
        units = yield in_parens.optional()

        # log.debug(
        #     "further desc line",
        #     grb=grp_label,
        #     var_labels=var_labels,
        #     units=units,
        # )
        var_descs = dict()
        for i in range(count):
            var_ind = lower + i
            dat = {'group_label': grp_label}
            if var_labels != None:
                dat['var_label'] = var_labels[i]
            if units != None:
                dat['units'] = units
            var_descs[var_ind] = dat

        # log.debug("parsing desc line", var_descs=var_descs)
        return var_descs

    return parse_line(wrap_whitespace(desc_line))

@generate
def state_desc_lines():

    count = yield state_dimension_line()
    var_groups = yield var_desc_line().at_least(3)
    vars = {k: v for g in var_groups for k, v in g.items()}

    return {
        'state_var': 'x',
        'xdim': count,
        'vars': vars,
    }

state_desc_block = parse_block("state_desc_block", state_desc_lines)


def control_dimension_line():
    """
    This parses lines like:
    ```
    Number of controls uc (0 <= uc <= 1): udim =   4
    ```
    """

    @generate
    def str_parser():
        yield string("Number of controls uc (0 <= uc <= 1): udim =")
        yield whitespace
        udim = yield digits
        return int(udim)

    return parse_line(wrap_whitespace(str_parser))

def control_channel_line():
    """
    This parses lines like:
    ```
     uc( 1 -  4) are control channels
    ```
    """

    @generate
    def channel_nums():
        """Parses: `uc( 7 - 10) are control channels`"""

        yield seq(string('uc('), whitespace.optional())
        lower = yield digits
        yield wrap_whitespace(string('-'))
        upper = yield digits
        yield seq(whitespace.optional(), string(')'))
        yield whitespace.optional()
        yield string("are control channels")
        return (int(lower), int(upper) + 1)

    return parse_line(wrap_whitespace(channel_nums))

def control_mapping_line():
    """
    This parses lines like:
    ```
    Propeller motor  4 controlled by uc channel  4 and powered by battery  1
    ```
    """

    @generate
    def channel_triple():
        yield wrap_whitespace(string("Propeller motor"))
        motor = yield digits
        yield wrap_whitespace(string("controlled by uc channel"))
        channel = yield digits
        yield wrap_whitespace(string("and powered by battery"))
        battery = yield digits
        return {
            'propeller_motor': int(motor),
            'uc_channel': int(channel),
            'battery': int(battery),
        }

    return parse_line(wrap_whitespace(channel_triple))

@generate
def control_desc_lines():
    udim = yield control_dimension_line()
    (lower, upper) = yield control_channel_line()
    mapping_list = yield control_mapping_line().many()
    channel_map = { mapping['uc_channel'] : mapping for mapping in mapping_list }

    return {
        'udim': udim,
        'channels': channel_map,
    }

control_desc_block = parse_block("control_desc_block", control_desc_lines)
