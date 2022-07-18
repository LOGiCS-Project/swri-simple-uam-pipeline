from attrs import define, field
from omegaconf import SI
from .manager import Config
from .path_config import PathConfig
from .workspace_config import ResultsConfig, WorkspaceConfig
from .service_config import ServiceConfig
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

    read_only : bool = field(
        default = False,
    )
    """
    Should the stub server be run as a read only database?
    """

    service : ServiceConfig = field(
        default = ServiceConfig(
            stdout_file = SI("${path:log_directory}/craidl_stub_db/stdout.log"),
            stderr_file = SI("${path:log_directory}/craidl_stub_db/stderr.log"),
        )
    )
    """
    Settings for running the stub server as a service.
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
        default=SI("localhost")
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

    static_corpus_cache : str = field(
        default=SI("${path:cache_directory}/static_corpus_cache"),
    )
    """
    The cache directory to use when generating a static corpus.
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

    conf_file = "craidl.conf.yaml",

    interpolation_key = "craidl",
)
