from attrs import define, field
from omegaconf import SI
from .manager import Config
from .path_config import PathConfig
from .craidl_config import CraidlConfig
from typing import List
from .workspace_config import ResultsConfig, WorkspaceConfig

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

    exclude : List[str] = ['.git']

    exclude_from : List[str] = []

    result_exclude : List[str] = ['.git']

    result_exclude_from : List[str] = []

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
