from attrs import define, field
from omegaconf import SI
from .manager import Config
from .path_config import PathConfig
from .craidl_config import CraidlConfig
from typing import List, Dict, Union
from .workspace_config import ResultsConfig, WorkspaceConfig

@define
class StudyParamsConfig():
    """
    Dataclass carrying configuration information for the study_params used in
    when processing a design.
    """

    field_order : List[str] = [
        "Analysis_Type",
        "Flight_Path",
        "CargoMass",
        "Requested_Lateral_Speed",
        "Requested_Vertical_Speed",
        "Requested_Vertical_Down_Speed",
        "Requested_Lateral_Acceleration",
        "Requested_Lateral_Deceleration",
        "Requested_Vertical_Acceleration",
        "Requested_Vertical_Deceleration",
        "Landing_Approach_Height",
        "Vertical_Landing_Speed",
        "Vertical_Landing_Speed_at_Ground",
        "Q_Position",
        "Q_Velocity",
        "Q_Angular_Velocity",
        "Q_Angles",
        "Ctrl_R",
    ]
    """
    Fields in the above list, when they exist in the provided params, will
    be written out in the above order to `study_params.csv`.

    Fields not mentioned above will appear afterwards in an arbitrary order.

    Fields from any provided study params are also checked against this list
    to catch simple formatting errors.
    """

    default : List[Dict[str,Union[int,float]]] = [
        {
            "Flight_Path": 1,
            "Requested_Vertical_Speed": 0,
            "Requested_Lateral_Speed": 46,
            "Q_Position": 1,
            "Q_Velocity": 1,
            "Q_Angular_Velocity": 1,
            "Q_Angles": 1,
            "Ctrl_R": 1
        },
        {
            "Flight_Path": 3,
            "Requested_Vertical_Speed": 0,
            "Requested_Lateral_Speed": 46,
            "Q_Position": 1,
            "Q_Velocity": 1,
            "Q_Angular_Velocity": 1,
            "Q_Angles": 1,
            "Ctrl_R": 0.9
        },
        {
            "Flight_Path": 4,
            "Requested_Vertical_Speed": -4,
            "Requested_Lateral_Speed": 0,
            "Q_Position": 1,
            "Q_Velocity": 1,
            "Q_Angular_Velocity": 1,
            "Q_Angles": 1,
            "Ctrl_R": 0.8
        },
        {
            "Flight_Path": 5,
            "Requested_Vertical_Speed": 0,
            "Requested_Lateral_Speed": 46,
            "Q_Position": 1,
            "Q_Velocity": 1,
            "Q_Angular_Velocity": 1,
            "Q_Angles": 1,
            "Ctrl_R": 0.7
        }
    ]
    """
    The default study parameters to use when no other study parameters were
    provided.

    This should be a list of dicts each containing what should end up being
    a row of the output CSV.
    """

@define
class D2CWorkspaceConfig(WorkspaceConfig):
    """
    A dataclass carrying configuration fields and defaults.
    As described here: https://omegaconf.readthedocs.io/en/2.1_branch/structured_config.html

    Most defaults are set in WorkspaceConfig but they can be overridden here.
    Likewise for ResultsConfig, just inherit from that class and set the
    default for `results` to your new class.
    """

    workspaces_dir : str = field(
        default=SI("${path:work_directory}/d2c_workspaces")
    )
    """
    Dir where workspaces are stored.
    """

    cache_dir : str = field(
        default=SI("${path:cache_directory}/d2c_workspaces")
    )
    """
    Dir for cached data.
    """

    max_workspaces : int = 1
    """
    The maximum number of workspaces operating simultaneously.

    Direct2Cad currently only supports one instance of Creo at a time per
    machine.
    """

    exclude : List[str] = ['.git']
    """
    Files and folders to exclude when creating the workspace.
    """

    result_exclude : List[str] = [
        '.git',
        # 'workingdir/*.prt', #copied part files
        'data.zip',
        '__pycache__',
    ]
    """
    Files and folders to exclude from the generated results file.
    """

    study_params : StudyParamsConfig = field(
        default=StudyParamsConfig()
    )
    """
    Config info for the study params using when processing a design.
    """

    copy_uav_parts : bool = False
    """
    Should the direct2cad workspace copy the parts from the athens uav repo?
    """

    # craidl : CraidlConfig = field(
    #     default=SI("${craidl:}")
    # )
    # """
    # The config to use for craidl in the workspace. Should interpolate into
    # the currently loaded craidl.conf.yaml by default.
    # """

# Add to the configuration manager
Config.register(
    D2CWorkspaceConfig, # class to be registered

    conf_deps = [PathConfig, CraidlConfig],
    # Config classes this can interpolate with.
    # e.g. If `PathConfig` is in `conf_deps` this config file (and the defaults)
    #      can use "${path:data_dir}/foo/bar.txt" and have it resolve correctly.

    conf_file = "d2c_workspace.conf.yaml",
    # The file that will be loaded to fill out this config class.
    # i.e. If you write: `example_int: 32` to "${path:config_dir}/uam_workspace.conf.yaml"
    #      then `Config[UAMWorkspaceConfig].example_int == 32`.

    interpolation_key = "d2c_workspace",
    # Key used by other config classes to access variables in this class.
    # e.g. If another config class registers `UAMWorkspaceConfig` in its
    #      `conf_deps`, it can use "${uam_workspace:example_str}"
    #      in its own definitions.
)
