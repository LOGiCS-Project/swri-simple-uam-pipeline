from attrs import define, field
from platformdirs import PlatformDirs
from pathlib import Path

dirs = PlatformDirs("SimpleUAM")

@define
class PathConfig():
    config_dir    : Path = Path(dirs.user_config_dir)
    data_dir      : Path = Path(dirs.user_data_dir)
    cache_dir     : Path = Path(dirs.user_cache_dir)
    log_dir       : Path = Path(dirs.user_log_dir)
    documents_dir : Path = Path(dirs.user_documents_dir)
    runtime_dir   : Path = Path(dirs.user_runtime_dir)

PATHCONFIG_INTERPOLATION_KEY = "path"
PATHCONFIG_FILE_NAME = "paths.conf.yaml"
