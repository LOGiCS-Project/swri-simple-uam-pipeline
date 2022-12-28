from parsy import *
from copy import deepcopy, copy
from ..line_parser import *
from ..block_parser import *
from ..util import *
from simple_uam.util.logging import get_logger
log = get_logger(__name__)

@generate
def lateral_motion_str_parser():
    """
    Parses lines like:
    ```
    Objective steady state speed is UVW world =     0.00    0.00    0.00 m/s =     0.00    0.00    0.00 miles per hour
    ```
    """

    result = yield format_parser(
        'Objective steady state speed is UVW world = '\
        '${uvw_meters} m/s = ${uvw_miles} miles per hour',
        uvw_meters= scientific.sep_by(whitespace,min=3,max=3),
        uvw_miles = scientific.sep_by(whitespace,min=3,max=3),
    )

    uvw_meters = result['uvw_meters']
    uvw_miles = result['uvw_miles']

    return {
        'u_north': {'value': uvw_meters[0], 'units':'m/s', 'mph': uvw_miles[0]},
        'v_east': {'value': uvw_meters[1], 'units':'m/s', 'mph': uvw_miles[1]},
        'w_down': {'value': uvw_meters[2], 'units':'m/s', 'mph': uvw_miles[2]},
    }

lateral_motion_line_parser = parse_strip_line(
    lateral_motion_str_parser
)

@generate
def turning_frame_str_parser():
    """
    Parses lines like:
    ```
    Objective steady state speed is UVW world =     1.00    0.00    0.00 m/s; PQR world =     0.00    0.00    0.00 rad/s
    ```
    """

    result = yield format_parser(
        'Objective steady state speed is UVW world = '\
        '${uvw} m/s; PQR world = ${pqr} rad/s',
        uvw = scientific.sep_by(whitespace,min=3,max=3),
        pqr = scientific.sep_by(whitespace,min=3,max=3),
    )

    uvw = result['uvw']
    pqr = result['pqr']

    return {
        'u_north': with_units(uvw[0], 'm/s'),
        'v_east': with_units(uvw[1], 'm/s'),
        'w_down': with_units(uvw[2], 'm/s'),
        'p_world': with_units(pqr[0], 'rad/s'),
        'q_world': with_units(pqr[1], 'rad/s'),
        'r_world': with_units(pqr[2], 'rad/s'),
    }

turning_frame_line_parser = parse_strip_line(
    turning_frame_str_parser
)

@generate
def turning_radius_str_parser():
    """
    Parses lines like:
    ```
    Turning radius     500.00 m (positive means clockwise looking down), Rworld =     0.0020 radians/s
    ```
    """

    fstring = "Turning radius     ${turn} m "\
        "(positive means clockwise looking down), "\
        "Rworld =     ${r} radians/s"

    result = yield format_parser(
        fstring,
        turn=scientific,
        r=scientific,
    )

    return {
        'turning_radius': with_units(result['turn'],'m'),
        'r_world': with_units(result['r'],'r/s'),
    }

turning_radius_line_parser = parse_strip_line(
    turning_radius_str_parser
)

@generate
def turning_motion_lines_parser():

    output = dict()

    output |= yield turning_frame_line_parser
    output |= yield turning_radius_line_parser

    return output

lwa_size_warning_line_parser = parse_strip_line(
    string('Warning: lwa not large enough').result(True)
).dtag('__warning__lwa_not_large_enough')

def unit_vars_line_parser(prefix, keys=None):
    """
    Parses lines like:
    ```
    <prefix> (<unit>) <num> ....
    ```

    with the appropriate headers
    """

    count = len(keys) if keys != None else 1

    base_parser = format_parser(
        # Just insert the prefix string directly so we get the benefits of
        # permissive whitespace.
        prefix + '$s?${units}$s?${vals}',
        units=in_parens.optional(None),
        vals=scientific.sep_by(whitespace, min=count, max=count),
    )

    @generate
    def unit_vars_str_parser():
        parsed = yield base_parser
        output = dict()
        # log.debug(
        #     "parsed_vals",
        #     parsed=parsed,
        # )
        if keys == None:
            output = with_units(parsed['vals'][0], parsed['units'])
        else:
            for (i, v) in enumerate(parsed['vals']):
                output[keys[i]] = with_units(v, parsed['units'])
        return output

    return parse_strip_line(unit_vars_str_parser)

uvw_vars_line_parser = unit_vars_line_parser(
    "UVW world, body",
    ['u_world','v_world','w_world','u_body','v_body','w_body'],
).dtag('uvw')

uvw_dot_vars_line_parser = unit_vars_line_parser(
    "UVWdot,PQRdot",
    ['u_dot','v_dot','w_dot','p_dot','q_dot','r_dot'],
).dtag('uvw_dot')

uvw_dot_warning_line_parser = parse_strip_line(
    format_parser(
        "Warning: at least one value of UVWdot or PQRdot "\
        "is large enough that steady flight is unlikely (not a trim state)."
    ).result(True)
).dtag('__warning__acceleration_too_high_for_trim_state')

roll_angle_vars_line_parser = unit_vars_line_parser(
    "Roll  angle phi",
).dtag('roll_angle')

pitch_angle_vars_line_parser = unit_vars_line_parser(
    "Pitch angle theta",
).dtag('pitch_angle')

thrust_vars_line_parser = unit_vars_line_parser(
    "Thrust world, body",
    ['u_world','v_world','w_world','u_body','v_body','w_body'],
).dtag('thrust')

lift_vars_line_parser = unit_vars_line_parser(
    "Lift world, body",
    ['u_world','v_world','w_world','u_body','v_body','w_body'],
).dtag('lift')

drag_vars_line_parser = unit_vars_line_parser(
    "Drag world, body",
    ['u_world','v_world','w_world','u_body','v_body','w_body'],
).dtag('drag')

trim_state_fixed_vars_line_parser = alt(
    uvw_vars_line_parser,
    uvw_dot_vars_line_parser,
    uvw_dot_warning_line_parser,
    roll_angle_vars_line_parser,
    pitch_angle_vars_line_parser,
    thrust_vars_line_parser,
    lift_vars_line_parser,
    drag_vars_line_parser,
)

csolve_str_parser = alt(
    string('MINPACK').result('minpack'),
    string('SIM/MIN').result('sim_min'),
    string('SIMPLEX').result('simplex'),
)

are_str_parser = string('ARE').result({}).exists('are')

def range_vars_line_parser(prefix, units=None):
    """
    Parses lines like:
    ```
    <prefix>(<units>) <lower> - <upper> <vals...>
    ```
    """

    @generate
    def range_vars_str_parser():

        r = yield format_parser(
            # Just insert the prefix string directly so we get the benefits of
            # permissive whitespace.
            prefix + '$s?${units}$s?${lower}$s?${dash}$s?${upper}$s?',
            units = in_parens.optional(None),
            lower = int_p,
            dash = string('-').optional(),
            upper = int_p,
        )

        lower = r['lower']
        upper = r['upper'] + 1
        count = upper - lower
        units_local = units if units else r['units']

        vals = yield scientific.sep_by(whitespace, min=count, max=count)

        output = dict()
        for (i, v) in enumerate(vals):
            output[lower + i] = with_units(v, units_local)

        return output

    return parse_strip_line(range_vars_str_parser)

wing_ld_range_line_parser = range_vars_line_parser(
    "Wing Ld"
).dtag('wing_ld')

wing_ld_warning_line_parser = parse_strip_line(
    format_parser(
        'Warning: at least one wing is loaded '\
        'beyond max load, hence structural failure likely.  Wings:$s?'\
        '${__warning__wings_overloaded}',
        __warning__wings_overloaded=int_p.sep_by(whitespace,min=1),
    )
)

controls_range_line_parser = range_vars_line_parser(
    "Controls"
).dtag('controls_uc')

controls_warning_line_parser = parse_strip_line(
    format_parser(
        'Caution: at least one control channel '\
        'is outside range of 0 < uc < 1, '\
        'hence steady flight may be unlikely.'
    ).result(True)
).dtag('__warning__control_channel_out_of_bounds')

motor_rpm_range_line_parser = range_vars_line_parser(
    "Motor RPM", units='rpm'
).dtag('motor_rpm')

motor_thrust_range_line_parser = range_vars_line_parser(
    "Thrust"
).dtag('motor_thrust')

motor_current_range_line_parser = range_vars_line_parser(
    "Motor Amps", units='amps'
).dtag('motor_current')

motor_current_warning_line_parser = parse_strip_line(
    format_parser(
        'Warning: at least one motor '\
        'maximum current exceeded.  Motors:$s?'\
        '${__warning__motors_overdrawing_current}',
        __warning__motors_overdrawing_current=int_p.sep_by(whitespace,min=1),
    )
)

motor_power_warning_line_parser = parse_strip_line(
    format_parser(
        'Warning: at least one motor '\
        'maximum power exceeded.  Motors:$s?'\
        '${__warning__motors_overdrawing_power}',
        __warning__motors_overdrawing_power=int_p.sep_by(whitespace,min=1),
    )
)

trim_state_range_vars_line_parser = alt(
    wing_ld_range_line_parser,
    wing_ld_warning_line_parser,
    controls_range_line_parser,
    controls_warning_line_parser,
    motor_rpm_range_line_parser,
    motor_thrust_range_line_parser,
    motor_current_range_line_parser,
    motor_current_warning_line_parser,
    motor_power_warning_line_parser,
)

trim_state_vars_lines_parser = alt(
    trim_state_fixed_vars_line_parser,
    trim_state_range_vars_line_parser,
).at_least(1).map(merge_dicts)

trim_state_vars_block_parser = parse_block(
    'trim_state_vars',
    trim_state_vars_lines_parser.map(collect_warnings),
)

@generate
def battery_info_str_parser():
    """
    Parses lines like:
    ```
    Battery # 1 Current =   34.679 amps,  Time to 20% charge remaining =  498.3 s,  Flight distance =      0.000 m
    ```
    """

    r = yield format_parser(
        'Battery #$s?${battery_num} Current = ${current} amps, '\
        'Time to 20% charge remaining = ${time_to_low_charge} s, '\
        'Flight distance = ${flight_distance} m${warning}',
        battery_num=int_p,
        current=scientific.with_units('amps'),
        time_to_low_charge=scientific.with_units('s'),
        flight_distance=scientific.with_units('m'),
        warning=(whitespace.optional() >> string('with warning')).exists(),
    )

    num = r.pop('battery_num')

    return {num: r}

battery_info_line_parser = parse_strip_line(
    battery_info_str_parser
).dtag('batteries')

battery_current_warning_line_parser = parse_strip_line(
    format_parser(
        'Caution: current exceeds contiuous '\
        'maximum for at least one of the batteries.'
    ).result(True)
).dtag('__warning__battery_overdrawing_current')

total_battery_info_line_parser = parse_strip_line(
    format_parser(
        'Total power from batteries ${total_battery_power} watts; '\
        'total power in motors ${total_motor_power} watts',
        total_battery_power=scientific.with_units('watts'),
        total_motor_power=scientific.with_units('watts'),
    )
)
"""
Parses lines like:
```
Total power from batteries     769.876 watts;  total power in motors     589.713 watts
```
"""

battery_info_lines_parser = alt(
    battery_info_line_parser,
    battery_current_warning_line_parser,
    total_battery_info_line_parser,
).union_many(min=1)

trim_state_battery_info_block_parser = parse_block(
    'trim_state_battery_info',
    battery_info_lines_parser.map(collect_warnings),
)

ricpack_are_returns_line_parser = parse_strip_line(
    format_parser(
        "RICPACK ARE solver returns Ind(1), Ind(2), CPERM(1): "\
        "${ind_1} ${ind_2} ${cperm_1} (Success = 0, 0, <1.e19)",
        ind_1=scientific,
        ind_2=scientific,
        cperm_1=scientific,
    )
)
"""
Parses lines like:
```
RICPACK ARE solver returns Ind(1), Ind(2), CPERM(1):            0           0   78631.764075311177       (Success = 0, 0, <1.e19)
```
"""

are_solve_failed_line_parser = parse_strip_line(
    string("ARE solve failed")
).not_exists('are_success')

@generate
def ricpack_are_lines_parser():

    are_output = dict()

    are_output |= yield ricpack_are_returns_line_parser
    are_output |= yield are_solve_failed_line_parser

    output = {'are_control': are_output}

    if not are_output['are_success']:
        output['__warning__are_solve_failed'] = True

    return output

controls_k_line_parser = parse_strip_line(
    format_parser("Controls K where uc = uc_trim + K(x - x_trim)")
)

controls_k_num_line_parser = parse_strip_line(
    scientific.sep_by(whitespace, min=12, max=12)
)
"""
parses lines like: -0.13226     1.26404     0.24207     0.91853     0.09374     0.44073     9.54655     0.98907     0.43939    -0.09109     0.86756     0.21431
"""

@generate
def controls_k_lines_parser():
    """
    Parses lines like:
    ```
    Controls K where uc = uc_trim + K(x - x_trim)
    -0.13226     1.26404     0.24207     0.91853     0.09374     0.44073     9.54655     0.98907     0.43939    -0.09109     0.86756     0.21431
    -1.27729     0.10265     0.24229     0.07202     0.93224    -0.42730     0.76451     9.66468    -0.42600    -0.87607     0.07080     0.21452
    -0.20734    -0.67425     0.76220    -0.48402     0.14297     0.55724    -5.06458     1.53362     0.55712    -0.14335    -0.46369     0.67386
     0.65669     0.23911     0.76210     0.16537    -0.47371    -0.56146     1.77031    -4.94259    -0.56132     0.45128     0.16526     0.67377
    ```
    """

    yield controls_k_line_parser

    nums = yield controls_k_num_line_parser.at_least(1)

    return {'controls_k': {i+1: v for (i,v) in enumerate(nums)}}

@generate
def xtrim_qskip_str_parser():

    yield string("xtrim, qskip") >> whitespace
    xtrim_qskip = yield scientific

    return xtrim_qskip

xtrim_qskip_line_parser = parse_strip_line(
    format_parser(
        "xtrim, qskip ${val}",
        val=scientific,
    )
)
"""
Parses lines like:
```
xtrim, qskip            0
```
"""

@generate
def xtrim_qskip_lines_parser():
    """
    Parses lines like:
    ```
    xtrim, qskip            0
     0.00000     0.00000     0.00000     0.00000     0.00000     0.00000     1.00000     0.00000    -0.00001     0.00000     0.00000     0.00000
    ```
    """

    xtrim_qskip = yield xtrim_qskip_line_parser
    xtrims = yield controls_k_num_line_parser

    return { 'xtrim': {
        'qskip': xtrim_qskip['val'],
        'xtrims': xtrims,
    }}

trim_state_controls_lines_parser = union_seq(
    ricpack_are_lines_parser,
    controls_k_lines_parser,
    xtrim_qskip_lines_parser,
)

trim_state_controls_block_parser = parse_block(
    'trim_state_controls',
    trim_state_controls_lines_parser.map(collect_warnings),
)
