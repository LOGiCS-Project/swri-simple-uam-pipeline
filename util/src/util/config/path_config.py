from attrs import define, field
from platformdirs import PlatformDirs

PATHCONFIG_INTERPOLATION_KEY = "path"
PATHCONFIG_FILE_NAME = "paths.conf.yaml"
APP_NAME = "SimpleUAM"

dirs = PlatformDirs(APP_NAME)


@define
class PathConfig:

    config_dir: str = field(
        default=dirs.user_config_dir,
        converter=str,
    )

    data_dir: str = field(
        default=dirs.user_data_dir,
        converter=str,
    )

    cache_dir: str = field(
        default=dirs.user_cache_dir,
        converter=str,
    )

    log_dir: str = field(
        default=dirs.user_log_dir,
        converter=str,
    )

    documents_dir: str = field(
        default=dirs.user_documents_dir,
        converter=str,
    )

    work_dir: str = field(
        default=dirs.user_runtime_dir,
        converter=str,
    )


"""
This particular config object is special and doesn't need an explicit
registration. We use the config_dir value to find a sequence of dirs to
load if neccesary, so it has to be handled separately from more standard
config objects.
"""
