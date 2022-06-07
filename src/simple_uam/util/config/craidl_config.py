from attrs import define, field
from omegaconf import SI
from .manager import Config
from .path_config import PathConfig
from .workspace_config import RecordsConfig, WorkspaceConfig
from typing import Optional

@define
class StubServerConfig():
    """
    Settings for the corpus stub server.
    """

    cache_dir : str = field(
        default=SI("${path:cache_directory}/corpus_stub_cache"),
    )
    """
    Cache for downloaded installers and static corpus dumps.
    """

    server_dir: str = field(
        default=SI("${path:data_directory}/corpus_stub_server")
    )
    """
    Dir where the gremlin stub server will be unpacked.
    """

    graphml_corpus : str = field(
        default=SI("${path:data_directory}/corpus_stub.graphml")
    )
    """
    The corpus to use with the stub server. Relative paths are assumed to be
    with respect to repo_root.
    """

    host : str = field(
        default='localhost',
    )
    """
    The host the stub server will server from.
    """

    port : int = field(
        default = 8182,
    )
    """
    The port the stub server will serve from.
    """

@define
class CraidlConfig():
    """
    Config properties for working with craidl and the gremlin stub server.
    """

    example_dir : Optional[str] = field(
        default=SI("${path:data_directory}/craidl_examples"),
    )
    """
    Dir containing craidl example designs (each in their own subfolder.)
    """

    stub_server : StubServerConfig = StubServerConfig()
    """
    Stub server settings.
    """

    server_host : str = field(
        default=SI("${stub_server.host}")
    )
    """
    The host to connect to when using a gremlin corpus server.
    """

    server_port : int = field(
        default = SI("${stub_server.port}")
    )
    """
    The port to connect to when using a gremlin corpus server.
    """

    static_corpus : str = field(
        default=SI("${path:data_directory}/corpus_static_dump.json"),
    )
    """
    The parsed static corpus to be generated/used when creating info files.
    """

    use_static_corpus : bool = True
    """
    Use the static corpus for generating design info files if true, otherwise
    use the server.
    """

# Add to the configuration manager
Config.register(
    CraidlConfig, # class to be registered

    conf_deps = [PathConfig],
    # Config classes this can interpolate with.
    # e.g. If `PathConfig` is in `conf_deps` this config file (and the defaults)
    #      can use "${path:data_dir}/foo/bar.txt" and have it resolve correctly.

    conf_file = "craidl.conf.yaml",
    # The file that will be loaded to fill out this config class.
    # i.e. If you write: `example_int: 32` to "${path:config_dir}/uam_workspace.conf.yaml"
    #      then `Config[UAMWorkspaceConfig].example_int == 32`.

    interpolation_key = "craidl",
    # Key used by other config classes to access variables in this class.
    # e.g. If another config class registers `UAMWorkspaceConfig` in its
    #      `conf_deps`, it can use "${uam_workspace:example_str}"
    #      in its own definitions.
)
