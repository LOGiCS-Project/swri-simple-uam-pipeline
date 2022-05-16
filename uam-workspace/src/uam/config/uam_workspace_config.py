from attrs import define, field
from util.config import Config, PathConfig
from util.paths import dependencies_dir
from .celery_config import CeleryConfig

@define
class UamWorkspaceConfig():
    """
    A dataclass carrying configuration fields and defaults.
    As described here: https://omegaconf.readthedocs.io/en/2.1_branch/structured_config.html
    """
    workspaces_dir : str = "${path:workspace_dir}/uam_workspaces"
    """ Directory containing all the workspaces """

    workspace_pattern : str = "workspace_{}"
    """
    The pattern for the subdirectory for each workspace, the {} will be
    replaced by a number.
    """

    max_workspaces : int = 4
    """ The maximum number of workspaces operating simultaneously """

    workspace_repo : str = str(dependencies_dir / 'athens_uav_workflows')
    """ The repo which the various local workspaces are copies of. """



# Add to the configuration manager
Config.register(
    UamWorkspaceConfig,
    interpolation_key = "uam_workspace",
    conf_file = "uam_workspace.conf.yaml",
    conf_deps = [PathConfig, CeleryConfig],
)
