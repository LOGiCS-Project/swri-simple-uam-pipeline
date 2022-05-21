from attrs import define, field
from util.config import Config, PathConfig

@define
class UAMWorkspaceConfig():
    """
    A dataclass carrying configuration fields and defaults.
    As described here: https://omegaconf.readthedocs.io/en/2.1_branch/structured_config.html
    """

    workspaces_dir : str = "${path:workspace_dir}/uam_workspaces"
    """ Directory containing all the workspaces """

    workspace_subdir_pattern : str = "workspace_{}"
    """
    The pattern for the subdirectory for each individual  workspace, the {}
    will be replaced by a number.
    """

    reference_subdir : str = "reference_workspace"
    """
    The subdirectory which contains the reference, unmodified copy of the
    workspace.
    """

    lock_subdir : str = "workspace_locks"
    """ Subdir of workspaces_dir where the various lockfiles are kept. """

    transaction_subdir : str = "transactions"
    """ Subdir of workspaces_dir for cached transaction results. """

    max_saved_transactions : int = -1
    """
    Number of transactions to save, with the oldest deleted first.
    Negative values mean transactions will never be deleted.
    """

    max_workspaces : int = 4
    """ The maximum number of workspaces operating simultaneously """

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
