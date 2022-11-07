from attrs import define, field
from omegaconf import SI
from .manager import Config
from .path_config import PathConfig
from .craidl_config import CraidlConfig
from .corpus_config import CorpusConfig
from pathlib import Path
from typing import List, Dict, Union, Optional
from .workspace_config import ResultsConfig, WorkspaceConfig

@define
class FDMEvalConfig(WorkspaceConfig):
    """
    A dataclass carrying configuration fields and defaults.
    As described here: https://omegaconf.readthedocs.io/en/2.1_branch/structured_config.html

    Most defaults are set in WorkspaceConfig but they can be overridden here.
    Likewise for ResultsConfig, just inherit from that class and set the
    default for `results` to your new class.
    """

    workspaces_dir : str = field(
        default=SI("${path:work_directory}/fdm_eval")
    )
    """
    Dir where workspaces are stored.
    """

    cache_dir : str = field(
        default=SI("${path:cache_directory}/fdm_eval")
    )
    """
    Dir for cached data.
    """

    namelist_to_json : List[str] = [
        'namelist.out',
    ]
    """
    Files to convert from namelist to json format in the output directory.
    """

    exclude : List[str] = [
        '.git',
        '.dockerignore',
        '.git*',
    ]
    """
    Files to not copy from the reference directory to each workspace.
    For FDM Build this is mostly about removing source control and
    documentation since we do want to copy files from autoreconf and
    configuration.
    """

    result_exclude : List[str] = []
    """
    Not relevant since we don't use Rsync to construct the results archive.
    """

    result_changed : Dict[str,str] = {
        'FlightDynamics/**': 'FlightDynamics/**',
    }
    """
    Files to include in the result archive if they have changed.
    """

    result_always : Dict[str,str] = {
        'metadata.json': 'metadata.json',
    }
    """
    A mapping from files in the FDM eval dir to those in the results archive
    that are always included when available even if no change is made.
    """

    nml_to_json : List[str] = [
        'flightDynFast.inp',
        'namelist.out',
    ]
    """
    Files in each run directory to convert from a namelist to json,
    by appending a '.json' extension.
    """

    path_to_csv : List[str] = [
        'path*.out',
    ]
    """
    Path files in each run directory to convert to their csv form.
    """

    fdm_dump_to_json : List[str] = [
        'flightDynFastOut.out',
        'metrics.out',
        'score.out',
    ]
    """
    FDM dump files in each run directory to convert to their json form.
    """

# Add to the configuration manager
Config.register(
    FDMEvalConfig, # class to be registered

    conf_deps = [PathConfig, CraidlConfig, CorpusConfig],
    # Config classes this can interpolate with.
    # e.g. If `PathConfig` is in `conf_deps` this config file (and the defaults)
    #      can use "${path:data_dir}/foo/bar.txt" and have it resolve correctly.

    conf_file = "fdm_eval.conf.yaml",
    # The file that will be loaded to fill out this config class.
    # i.e. If you write: `example_int: 32` to "${path:config_dir}/uam_workspace.conf.yaml"
    #      then `Config[UAMWorkspaceConfig].example_int == 32`.

    interpolation_key = "fdm_eval",
    # Key used by other config classes to access variables in this class.
    # e.g. If another config class registers `UAMWorkspaceConfig` in its
    #      `conf_deps`, it can use "${uam_workspace:example_str}"
    #      in its own definitions.
)
