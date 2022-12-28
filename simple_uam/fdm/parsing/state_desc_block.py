from parsy import *
from .line_parser import *
from .block_parser import *
from .util import *
from simple_uam.util.logging import get_logger
from attrs import define, field
log = get_logger(__name__)

state_dimension_line_parser = parse_strip_line(
    format_parser(
        'Number of state variables x: xdim = ${xdim}',
        xdim = int_p,
    )
)
"""
This parses lines like:
```
Number of state variables x: xdim =  18
```
"""

@generate
def dimension_range_str_parser():

    printed = yield format_parser(
        '($s?${lower}$s?-$s?${upper}$s?)',
        lower=int_p,
        upper=int_p,
    )

    return (printed['lower'], printed['upper'] + 1)

label_str_parser = not_chars(":,()")

@generate
def label_w_note_str_parser():
    """Parses: `P about x (roll rate)`"""

    text = yield label_str_parser
    yield whitespace.optional()
    note = yield in_parens

    return f"{text.strip()} ({note.strip()})"

def sub_labels_str_parser(count):

    sep = wrap_whitespace(string(','))

    times_count = lambda p: p.sep_by(sep, min=count, max=count)

    return alt(
        times_count(label_w_note_str_parser),
        times_count(label_str_parser),
    )

def group_notes_str_parser(lower, upper):
    """
    Parses string like: `velocity in body frame: U forward, V right, W down (m/s)`
    """

    count = upper - lower

    @generate
    def grp_notes_internal_parser():
        group_label = yield alt(
            label_w_note_str_parser,
            label_str_parser,
        ) << whitespace.optional()

        var_labels = yield (
            string(':') >> whitespace >> sub_labels_str_parser(count)
        ).optional(None) << whitespace.optional()

        units = yield in_parens.optional(None)

        vars_info = dict()

        for (i, xvar) in enumerate(range(lower, upper)):

            var_info = {'group_label': group_label}

            if sub_label != None:
                var_info['var_label'] = var_labels[i]

            if units != None:
                var_into['units'] = units

            vars_info[xvar] = var_info

        return vars_info

    return grp_notes_internal_parser

@generate
def var_desc_str_parser():
    """
    This parses lines like:
    ```
     x( 1 -  3) is velocity in body frame: U forward, V right, W down (m/s)
     x( 4 -  6) is angular velocity in body frame: P about x (roll rate), Q about y (pitch rate), R about z (yaw rate) (radians/s)
     x( 7 - 10) is quaternion connecting world frame to body frame: q0, q1, q2, q3
    ```
    """

    yield string('x')

    (lower, upper) = yield dimension_range_str_parser

    yield wrap_whitespace(string('is'))

    grp_notes = yield grp_notes_str_parser(lower, upper)

    return grp_notes

var_desc_line_parser = parse_strip_line(var_desc_str_parser)

@generate
def state_desc_lines_parser():
    """
    Parses lines like:
    ```
    Number of state variables x: xdim =  18
     x( 1 -  3) is velocity in body frame: U forward, V right, W down (m/s)
     x( 4 -  6) is angular velocity in body frame: P about x (roll rate), Q about y (pitch rate), R about z (yaw rate) (radians/s)
     x( 7 - 10) is quaternion connecting world frame to body frame: q0, q1, q2, q3
     x(11 - 13) is world frame displacement:  X north, Y east, Z down (m)
     x(14 - 17) is motor angular speed (one for each motor) (radians/s)
     x(18 - 18) is battery charge (one for each battery) (amp seconds)
    ```
    """

    output = dict()

    output |= yield state_dimension_line_parser
    output |= yield var_desc_line_parser.union_many(min=3)

    return output

state_desc_block = parse_block("state_desc_block", state_desc_lines_parser)

control_dimension_line_parser = parse_strip_line(
    format_parser(
        'Number of controls uc (0 <= uc <= 1): udim =   ${udim}',
        udim = int_p,
    )
)
"""
This parses lines like:
```
Number of controls uc (0 <= uc <= 1): udim =   4
```
"""

control_desc_line_parser = parse_strip_line(
    format_parser(
        'uc${dims} are control channels',
        dims=dimension_range_str_parser,
    )
)
"""
This parses lines like:
```
 uc( 1 -  4) are control channels
```
"""

control_prop_line_parser = parse_strip_line(
    format_parser(
        'Propeller motor  ${motor} '\
        'controlled by uc channel  ${uc_channel} '\
        'and powered by battery  ${battery}',
        motor=int_p,
        uc_channel=int_p,
        battery=int_p,
    )
)
"""
This parses lines like:
```
Propeller motor  4 controlled by uc channel  4 and powered by battery  1
```
"""

control_wing_line_parser = parse_strip_line(
    format_parser(
        'Wing ${wing} servo ${servo} '\
        'controlled by uc channel ${uc_channel} '\
        ' with bias ${bias}',
        wing=int_p,
        servo=int_p,
        uc_channel=int_p,
        bias=scientific,
    )
)
"""
This parses lines like:
```
Wing 4 servo  4 controlled by uc channel  4 with bias 2.003
```
"""

@generate
def control_channel_line_parser():

    params = yield tag_alt(
        'channel_type',
        propeller=control_prop_line_parser,
        wing=control_wing_line_parser,
    )

    uc_channel = params.pop('uc_channel')

    return {uc_channel: params}

@generate
def control_desc_lines_parser():

    output = dict()

    output |= yield control_dimension_line_parser
    yield control_desc_line_parser
    output |= yield control_channel_line_parser.union_many(min=1)

    return output

control_desc_block = parse_block(
    "control_desc_block",
    control_desc_lines_parser
)

@generate
def parameters_lines_parser():
    """
    Parses blocks like:
    ```
    Number of state variables x: xdim =  18
        x( 1 -  3) is velocity in body frame: U forward, V right, W down (m/s)
        x( 4 -  6) is angular velocity in body frame: P about x (roll rate), Q about y (pitch rate), R about z (yaw rate) (radians/s)
        x( 7 - 10) is quaternion connecting world frame to body frame: q0, q1, q2, q3
        x(11 - 13) is world frame displacement:  X north, Y east, Z down (m)
        x(14 - 17) is motor angular speed (one for each motor) (radians/s)
        x(18 - 18) is battery charge (one for each battery) (amp seconds)
    Number of controls uc (0 <= uc <= 1): udim =   4
        uc( 1 -  4) are control channels
                    Propeller motor  1 controlled by uc channel  1 and powered by battery  1
                    Propeller motor  2 controlled by uc channel  2 and powered by battery  1
                    Propeller motor  3 controlled by uc channel  3 and powered by battery  1
                    Propeller motor  4 controlled by uc channel  4 and powered by battery  1
    ```
    """

    output = dict()

    output |= yield state_desc_lines_parser.dtag('state_variables')
    output |= yield control_desc_lines_parser.dtag('control_channels')

    return output

parameters_block = parse_block('parameters_block', parameters_lines_parser)
