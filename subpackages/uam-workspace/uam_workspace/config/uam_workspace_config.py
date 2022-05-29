from attrs import define, field
from util.config import Config, PathConfig, SI
from ..generic.config import RecordsConfig, WorkspaceConfig


@define
class UAMWorkspaceConfig(WorkspaceConfig):
    """
    A dataclass carrying configuration fields and defaults.
    As described here: https://omegaconf.readthedocs.io/en/2.1_branch/structured_config.html

    Most defaults are set in WorkspaceConfig but they can be overridden here.
    Likewise for RecordsConfig, just inherit from that class and set the
    default for `records` to your new class.
    """

    workspaces_dir : str = field(
        default=SI("${path:work_dir}/uam_workspaces")
    )

# Add to the configuration manager
Config.register(
    UAMWorkspaceConfig, # class to be registered

    conf_deps = [PathConfig],
    # Config classes this can interpolate with.
    # e.g. If `PathConfig` is in `conf_deps` this config file (and the defaults)
    #      can use "${path:data_dir}/foo/bar.txt" and have it resolve correctly.

    conf_file = "uam_workspace.conf.yaml",
    # The file that will be loaded to fill out this config class.
    # i.e. If you write: `example_int: 32` to "${path:config_dir}/uam_workspace.conf.yaml"
    #      then `Config[UAMWorkspaceConfig].example_int == 32`.

    interpolation_key = "uam_workspace",
    # Key used by other config classes to access variables in this class.
    # e.g. If another config class registers `UAMWorkspaceConfig` in its
    #      `conf_deps`, it can use "${uam_workspace:example_str}"
    #      in its own definitions.
)
