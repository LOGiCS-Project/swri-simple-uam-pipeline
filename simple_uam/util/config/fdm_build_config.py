from attrs import define, field
from omegaconf import SI
from .manager import Config
from .path_config import PathConfig
from .craidl_config import CraidlConfig
from typing import List, Dict, Union, Optional
from .workspace_config import ResultsConfig, WorkspaceConfig

@define
class FDMBuildCacheConfig():
    """
    Configuring for the build cache which keeps copies of previously built
    FDM executables for efficiency's sake.
    """

    enable : bool = True
    """
    Do we cache build products at all or just rebuild them whenever required?
    """

    subdir : str = "bin_archives"
    """
    The directory in which all the cached binaries from previous runs of
    fdm build are stored.

    If a relative path is provided, it is assumed to be a subdirectory of
    the FDM build cache directory.
    """

    max_count : int = 1000
    """
    The number of FDM executables to preserve in the local cache.
    Negative values mean transactions will never be deleted.
    Zero means that transactions won't be saved at all
    (and produced only lazily)

    Note that cleanup is only triggered when overflow is >10% or at least
    5 items, whichever is larger.
    """

@define
class FDMBuildConfig(WorkspaceConfig):
    """
    A dataclass carrying configuration fields and defaults.
    As described here: https://omegaconf.readthedocs.io/en/2.1_branch/structured_config.html

    Most defaults are set in WorkspaceConfig but they can be overridden here.
    Likewise for ResultsConfig, just inherit from that class and set the
    default for `results` to your new class.
    """

    workspaces_dir : str = field(
        default=SI("${path:work_directory}/fdm_build")
    )
    """
    Dir where workspaces are stored.
    """

    cache_dir : str = field(
        default=SI("${path:cache_directory}/fdm_build")
    )
    """
    Dir for cached data.
    """

    exclude : List[str] = [
        '.git',
        'doc',
        '.dockerignore',
        '.git*',
        'copy_dlls*',
        '*.md',
    ]
    """
    Files to not copy from the reference directory to each workspace.
    For FDM Build this is mostly about removing source control and
    documentation since we do want to copy files from autoreconf and
    configuration.
    """

    result_exclude : List[str] = [
        'THIS FIELD ISN\'T USED IN FDM BUILD',
        'BECAUSE RSYNC ISN\'T USED TO CONSTRUCT',
        'THE RESULTS ARCHIVE',
    ]
    """
    Not relevant since we don't use Rsync to construct the results archive.
    """

    force_autoreconf : bool = False
    """
    Should each build force a new run of autoreconf? If false then autoreconf
    is performed in the reference directory and copied over to each
    workspace.

    Implies force_configure if true.

    Note: This setting can be overridden on a per-build basis.
    """

    autoreconf_timeout : Optional[int] = None
    """
    Timeout, in seconds, for the autoreconf phase of building an FDM executable.
    Defaults to no timeout.
    """

    force_configure : bool = False
    """
    Should configure be run on each build? If false then configuration if
    performed once in the reference directory and copied over to each workspace.

    Note: This setting can be overridden on a per-build basis.
    """

    configure_timeout : Optional[int] = None
    """
    Timeout, in seconds, for the autoreconf phase of building an FDM executable.
    Defaults to no timeout.
    """

    make_timeout : Optional[int] = None
    """
    Timeout, in seconds, for the make phase of building an FDM executable.
    Defaults to no timeout.
    """

    collect_dlls : bool = True
    """
    Should we collect dlls for the built executable and include them in the
    results archive?
    """

    user_files : List[str] = [
        'new_fdm/include/*.h',
        'new_fdm/src/*.f',
        'external_autopilot/include/*.h',
        'external_autopilot/src/*.c',
        'external_autopilot/src/*.f',
    ]
    """
    The set of alternate files (and globs) a user can provide when making calls
    to FDM build. These will replace matching files in the root FDM build dir.

    Note that only files already found within the reference workspace are
    allowed.

    Also, all files should be basic text files that can be encoded as a JSON
    string.
    """

    result_changed : Dict[str,str] = {
        'external_autopilot/**': 'src/external_autopilot/**',
        'new_fdm/**': 'src/new_fdm/**',
    }
    """
    A mapping from files in the FDM build dir to those in the results archive
    that are included when there is a change in the input file.
    """

    result_always : Dict[str,str] = {
        "bin/**": "**",
        'external_autopilot/src/*.c': 'src/external_autopilot/src/*.c',
        'external_autopilot/src/*.f': 'src/external_autopilot/src/*.f',
        '*.json': '*.json',
        '*.stdout': '*.stderr',
        '*.stderr': '*.stderr',
        '*.log': '*.log',
    }
    """
    A mapping from files in the FDM build dir to those in the results archive
    that are always included when available even if no change is made.
    """

    bin_cache : FDMBuildCacheConfig = FDMBuildCacheConfig()
    """
    Settings for the cache of FDM executables.
    """

    @property
    def cache_path(self):
        """ Path form of the general cache dir """
        return Path(self.cache_dir).resolve()

    @property
    def bin_cache_path(self):
        """ Resolved location of executable binary cache """
        base = Path(self.bin_cache.subdir)
        if base.is_absolute():
            return base.resolve()
        else:
            return (self.cache_path / base).resolve()

    @property
    def bin_cache_lockdir(self):
        """ The lock directory used for the binary cache """
        return self.bin_cache_path / "locks"

    @property
    def bin_cache_lockfile(self):
        """ The lockfile used for the binary cache """
        return self.bin_cache_lockdir / "cache.lock"


# Add to the configuration manager
Config.register(
    FDMBuildConfig, # class to be registered

    conf_deps = [PathConfig, CraidlConfig],
    # Config classes this can interpolate with.
    # e.g. If `PathConfig` is in `conf_deps` this config file (and the defaults)
    #      can use "${path:data_dir}/foo/bar.txt" and have it resolve correctly.

    conf_file = "fdm_build.conf.yaml",
    # The file that will be loaded to fill out this config class.
    # i.e. If you write: `example_int: 32` to "${path:config_dir}/uam_workspace.conf.yaml"
    #      then `Config[UAMWorkspaceConfig].example_int == 32`.

    interpolation_key = "fdm_build",
    # Key used by other config classes to access variables in this class.
    # e.g. If another config class registers `UAMWorkspaceConfig` in its
    #      `conf_deps`, it can use "${uam_workspace:example_str}"
    #      in its own definitions.
)
