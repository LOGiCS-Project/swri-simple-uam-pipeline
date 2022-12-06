from parsy import *
from copy import deepcopy, copy
from .line_parser import *
from .block_parser import *
from .util import *
from simple_uam.util.logging import get_logger
log = get_logger(__name__)

minpack_prefix_lines = static_lines(
    """
    This routine finds steady solutions for lateral speeds of 0 to 50 m/s (Unorth).
    (If steady climbing is desired, set the appropriate wind speed Wdwind (positive down)).
    A steady state (trimmed) flight condition is achieved when UVWdot and PQRdot are zero.
    It is assumed that the flight direction is X and there is no yaw (psi = 0) or roll (phi = 0).
    Motor amps also includes amps lost in the ESC.
    """
)

@generate
def aircraft_simplex_str_parser():
    """
    Parses lines like:
    ```
    aircraft%simplex =   2 (0 = minpack/simplex + previous convergence, 1 = simplex + previous convergence, 2 = simplex + 0.5 start).
    ```
    """

    fstring = "aircraft%simplex = ${a_simp} (0 = minpack/simplex + previous convergence, 1 = simplex + previous convergence, 2 = simplex + 0.5 start)."
    result = yield format_parser(fstring, a_simp=digits)
    return {'aircraft_simplex' : int(result['a_simp'])}

@generate
def objective_str_parser():
    """
    Parses lines like:
    ```
    Objective steady state speed is UVW world =     0.00    0.00    0.00 m/s =     0.00    0.00    0.00 miles per hour
    ```
    """

    yield whitespace.optional()
    yield string("Objective steady state speed is UVW world =")

    u_meters = yield whitespace >> scientific
    v_meters = yield whitespace >> scientific
    w_meters = yield whitespace >> scientific
    yield whitespace >> string("m/s") >> whitespace >> string("=")
    u_miles = yield whitespace >> scientific
    v_miles = yield whitespace >> scientific
    w_miles = yield whitespace >> scientific
    yield whitespace >> string("miles per hour")

    return {'steady_state_speed': {
        'u': {'m/s': u_meters, 'mph': u_miles},
        'v': {'m/s': v_meters, 'mph': v_miles},
        'w': {'m/s': w_meters, 'mph': w_miles},
    }}

objective_line_parser = parse_strip_line(objective_str_parser)

@generate
def simplex_pass_str_parser():
    """
    Parses lines like:
    ```
    SIMPLEX pass, max xd, fdcost, previous, used, iter   1 -1.611793669520136E-04  7.751070881881508E-06 F Y   511
    ```
    """

    sep = wrap_whitespace(string(","))

    initial_key = "SIMPLEX pass"

    other_keys = [
        "max xd",
        "fdcost",
        "previous",
        "used",
        "iter",
    ]

    keys = [initial_key]
    yield (string(initial_key) << sep)
    keys += yield string_from(*other_keys).sep_by(sep)

    output = dict()
    for key in keys:
        output[key] = yield whitespace >> (scientific | not_space.at_least(1).concat())

    return output

simplex_pass_line_parser = parse_strip_line(simplex_pass_str_parser)

@generate
def finished_minpack_str_parser():
    """
    Parses lines like:
    ```
    Finished  MINPACK lmdif1 call; info =  0 (should be 1, 2 or 3; see MINPACK documentation)
    ```
    """

    yield string("Finished  MINPACK lmdif1 call; info =")
    yield whitespace
    info = yield digits
    yield whitespace
    yield string("(should be 1, 2 or 3; see MINPACK documentation)")

    return {'finished_minpack' : {'info': int(info)}}

finished_minpack_line_parser = parse_strip_line(finished_minpack_str_parser)

@generate
def solver_summary_str_parser():
    """
    Parses lines like:
    ```
    Nonlinear SIMPLEX invoked 1 time(s): total iterations =   511
    ```
    """

    yield string("Nonlinear SIMPLEX invoked") >> whitespace
    invocations = yield digits
    yield wrap_whitespace(string("time(s): total iterations ="))
    iterations = yield digits

    return {
        'solver_summary': {
            'iterations': int(iterations),
            'invocations': int(invocations),
        }
    }

solver_summary_line_parser = parse_strip_line(solver_summary_str_parser)

def parse_unit_vars_line(prefix, ident, keys):
    """
    Parses lines like:
    ```
    <prefix> (<unit>) <num> ....
    ```

    with the appropriate headers
    """

    @generate
    def unit_vars_str_parser():
        yield string(prefix)
        yield whitespace
        unit = yield in_parens
        output = dict()
        for k in keys:
            output[k] = yield whitespace >> scientific

        output['units'] = unit
        return {ident: output}

    return parse_strip_line(unit_vars_str_parser)

uvw_vars_parser = parse_unit_vars_line(
    "UVW world, body", 'uvw',
    ['u_world','v_world','w_world','u_body','v_body','w_body'],
)

@generate
def uvw_dot_vars_parser():

    output = yield parse_unit_vars_line(
        "UVWdot,PQRdot", 'uvw_dot',
        ['u_dot','v_dot','w_dot','p_dot','q_dot','r_dot'],
    )

    output['uvw_dot']['warning'] = yield parse_strip_line(
        string("Warning: at least one value of UVWdot or PQRdot is large enough that steady flight is unlikely (not a trim state).")
    ).result(True).optional(False)

    return output

pitch_angle_vars_parser = parse_unit_vars_line(
    "Pitch angle theta", 'pitch_angle', ['pitch_angle'],
)

thrust_vars_parser = parse_unit_vars_line(
    "Thrust world, body", 'thrust',
    ['u_world','v_world','w_world','u_body','v_body','w_body'],
)

lift_vars_parser = parse_unit_vars_line(
    "Lift world, body", 'lift',
    ['u_world','v_world','w_world','u_body','v_body','w_body'],
)

drag_vars_parser = parse_unit_vars_line(
    "Drag world, body", 'drag',
    ['u_world','v_world','w_world','u_body','v_body','w_body'],
)

any_vars_parser = alt(
    uvw_vars_parser,
    uvw_dot_vars_parser,
    pitch_angle_vars_parser,
    thrust_vars_parser,
    lift_vars_parser,
    drag_vars_parser,
)

def parse_count_num_line(prefix, ident):
    """
    Parses lines like:
    ```
    <prefix>(<unit>) <lower> - <upper> <numbers>
    ```
    """

    @generate
    def count_num_str_parser():
        yield string(prefix) >> whitespace.optional()
        unit = yield in_parens.optional()
        yield whitespace
        lower = yield digits
        yield whitespace.optional() >> string('-') >> whitespace.optional()
        upper = yield digits

        lower = int(lower)
        upper = int(upper) + 1
        nums = dict()

        for i in range(lower, upper):
            yield whitespace
            num = yield scientific
            nums[i] = num

        output = dict(
            lower=lower,
            upper=upper,
            values=nums,
        )

        if unit:
            output['units'] = unit

        return {ident : output}

    return parse_strip_line(count_num_str_parser)

wing_ld_nums_parser = parse_count_num_line("Wing Ld", "wing_ld")
controls_nums_parser = parse_count_num_line("Controls", "controls")
motor_rpm_nums_parser = parse_count_num_line("Motor RPM", "motor_rpm")
thrust_nums_parser = parse_count_num_line("Thrust", "thrust")
motor_amps_nums_parser = parse_count_num_line("Motor Amps", "motor_amps")

any_nums_parser = alt(
    wing_ld_nums_parser,
    controls_nums_parser,
    motor_rpm_nums_parser,
    thrust_nums_parser,
    motor_amps_nums_parser,
)

@generate
def battery_info_str_parser():
    """
    Parses lines like:
    ```
    Battery # 1 Current =   34.679 amps,  Time to 20% charge remaining =  498.3 s,  Flight distance =      0.000 m
    ```
    """

    @generate
    def pair_parser():
        key = yield not_char("=").at_least(1).concat()
        yield wrap_whitespace(string('='))
        val = yield scientific
        yield whitespace
        unit = yield not_char(',').at_least(1).concat()

        key = to_undercase(key.strip())

        return {
            key : {
                'value': val,
                'unit' : unit.strip(),
            }
        }

    sep_parser = string(',') << whitespace.optional()

    results = pair_parser.sep_by(sep_parser, min=3)

    return {k:v for s in results for k, v in s.items()}

battery_info_line_parser = parse_strip_line(battery_info_str_parser)

@generate
def total_battery_info_str_parser():
    """
    Parses lines like:
    ```
    Total power from batteries     769.876 watts;  total power in motors     589.713 watts
    ```
    """

    yield string("Total power from batteries") << whitespace
    battery = yield scientific
    yield whitespace
    battery_units = yield not_char(";").at_least(1).concat()
    yield wrap_whitespace(string("total power in motors"))
    motors = yield scientific
    yield whitespace
    motors_units = yield any_char.at_least(1).concat()

    return {
        'total_battery_power': {
            'value': battery,
            'units': battery_units,
        },
        'total_motor_power': {
            'value': motors,
            'units': motors_units,
        },
    }

total_battery_info_line_parser = parse_strip_line(total_battery_info_str_parser)

@generate
def ricpack_are_str_parser():
    """
    Parses lines like:
    ```
    RICPACK ARE solver returns Ind(1), Ind(2), CPERM(1):            0           0   78631.764075311177       (Success = 0, 0, <1.e19)
    ```
    """

    yield string("RICPACK ARE solver returns Ind(1), Ind(2), CPERM(1):")
    ind_1 = yield whitespace >> scientific
    ind_2 = yield whitespace >> scientific
    cperm_1 = yield whitespace >> scientific
    yield whitespace >> string("(Success = 0, 0, <1.e19)")

    return {
        'ind_1': ind_1,
        'ind_2': ind_2,
        'cperm_1': cperm_1,
    }

ricpack_are_line_parser = parse_strip_line(ricpack_are_str_parser)

@generate
def cperm_str_parser():
    """
    Parses lines like:
    ```
    CPERM = 123.456
    ```
    """

    yield string("CPERM =") << whitespace
    cperm = yield scientific

    return {'cperm': cperm}

cperm_line_parser = parse_strip_line(cperm_str_parser)

are_solve_failed_line_parser = parse_strip_line(string("ARE solve failed"))\
    .result({'are_solve': False}).optional({'are_solve': True})

controls_k_line_parser = parse_strip_line(
    string("Controls K where uc = uc_trim + K(x - x_trim)"))

# lines like: -0.13226     1.26404     0.24207     0.91853     0.09374     0.44073     9.54655     0.98907     0.43939    -0.09109     0.86756     0.21431
controls_k_num_line_parser = parse_strip_line(
    scientific.sep_by(whitespace, min=12, max=12))

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

    return {'controls_k': nums}

@generate
def xtrim_qskip_str_parser():
    """
    Parses lines like:
    ```
    xtrim, qskip            0
    ```
    """

    yield string("xtrim, qskip") >> whitespace
    xtrim_qskip = yield scientific

    return xtrim_qskip

xtrim_qskip_line_parser = parse_strip_line(xtrim_qskip_str_parser)

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

    return { 'xtrim_qskip': {
        'value': xtrim_qskip,
        'xtrims': xtrims,
    }}


@generate
def minpack_trim_lines():
    """
    Parses blocks like:
    ```
    Objective steady state speed is UVW world =     0.00    0.00    0.00 m/s =     0.00    0.00    0.00 miles per hour
    SIMPLEX pass, max xd, fdcost, previous, used, iter   1 -1.611793669520136E-04  7.751070881881508E-06 F Y   511
    Finished  MINPACK lmdif1 call; info =  0 (should be 1, 2 or 3; see MINPACK documentation)
    Nonlinear SIMPLEX invoked 1 time(s): total iterations =   511
    UVW world, body   (m/s)       0.00000000       0.00000000       0.00000000       0.00000000       0.00000000       0.00000000
    UVWdot,PQRdot (m|r/s^2)       0.00010018       0.00000000       0.00003766      -0.00002326      -0.00002420      -0.00019932
    Pitch angle theta (deg)      -0.00058568
    Thrust world, body  (N)       0.00021248       0.00000000     -20.78639861       0.00000000       0.00000000     -20.78639861
    Lift world, body    (N)       0.00000000       0.00000000       0.00000000       0.00000000       0.00000000       0.00000000
    Drag world, body    (N)       0.00000000       0.00000000      -0.00000000      -0.00000000      -0.00000000      -0.00000000
    Wing Ld(N)  1 -  0
    Controls    1 -  4            0.28781383       0.28784064       0.84694532       0.84692654
    Motor RPM   1 -  4         5424.43186047    5424.91855202   15067.34264019   15067.06866778
    Thrust (N)  1 -  4            1.19001923       1.19023322       9.20324803       9.20289812
    Motor Amps  1 -  4            2.53120081       2.53156207      14.80861254      14.80773380
    Battery # 1 Current =   34.679 amps,  Time to 20% charge remaining =  498.3 s,  Flight distance =      0.000 m
    Total power from batteries     769.876 watts;  total power in motors     589.713 watts
    RICPACK ARE solver returns Ind(1), Ind(2), CPERM(1):            0           0   78631.764075311177       (Success = 0, 0, <1.e19)
    Controls K where uc = uc_trim + K(x - x_trim)
    -0.13226     1.26404     0.24207     0.91853     0.09374     0.44073     9.54655     0.98907     0.43939    -0.09109     0.86756     0.21431
    -1.27729     0.10265     0.24229     0.07202     0.93224    -0.42730     0.76451     9.66468    -0.42600    -0.87607     0.07080     0.21452
    -0.20734    -0.67425     0.76220    -0.48402     0.14297     0.55724    -5.06458     1.53362     0.55712    -0.14335    -0.46369     0.67386
     0.65669     0.23911     0.76210     0.16537    -0.47371    -0.56146     1.77031    -4.94259    -0.56132     0.45128     0.16526     0.67377
    xtrim, qskip            0
     0.00000     0.00000     0.00000     0.00000     0.00000     0.00000     1.00000     0.00000    -0.00001     0.00000     0.00000     0.00000
    ```
    """
    output = dict()
    output |= yield objective_line_parser

    output['solver_passes'] = yield simplex_pass_line_parser.at_least(1)
    output |= yield finished_minpack_line_parser
    output |= yield solver_summary_line_parser

    unit_vars = yield any_vars_parser.at_least(1)

    output['global_params'] = {k : v for d in unit_vars for k, v in d.items()}

    control_vars = yield any_nums_parser.at_least(1)

    output['control_params'] = {k : v for d in control_vars for k, v in d.items()}

    output |= yield battery_info_line_parser

    output |= yield total_battery_info_line_parser

    output |= yield ricpack_are_line_parser.optional({})

    output |= yield cperm_str_parser.optional({})

    # Has the optional already included
    output |= yield are_solve_failed_line_parser

    output |= yield controls_k_lines_parser.optional({})

    output |= yield xtrim_qskip_lines_parser.optional({})

    return output

minpack_trim_block = parse_block('minpack_trim',  minpack_trim_lines)
