
from attrs import define, field
from platformdirs import PlatformDirs
from pathlib import Path

PATHCONFIG_INTERPOLATION_KEY = "path"
PATHCONFIG_FILE_NAME = "paths.conf.yaml"
APP_NAME = "SimpleUAM"

dirs = PlatformDirs(APP_NAME)

@define
class PathConfig:

    config_directory: str = field(
        default=str(dirs.site_config_path / 'config'),
        converter=str,
    )

    cache_directory: str = field(
        default=str(dirs.site_data_path / 'cache'),
        converter=str,
    )

    log_directory: str = field(
        default=dirs.user_log_dir,
        converter=str,
    )

    work_directory: str = field(
        default=str(dirs.site_data_path),
        converter=str,
    )

    data_directory: str = field(
        default=str(dirs.site_data_path / 'data'),
        converter=str,
    )

    @property
    def repo_dir(self):
        """ Repository root dir. """
        return Path(__file__).resolve().parent.parent.parent.parent.parent

    @property
    def config_dir(self):
        """ Config file root dir. """
        return Path(self.config_directory)

    @property
    def cache_dir(self):
        """ Cache Directory. """
        return Path(self.cache_directory)

    @property
    def log_dir(self):
        """ Log Storage Directory. """
        return Path(self.log_directory)

    @property
    def work_dir(self):
        """ Working directory for assorted operations. """
        return Path(self.work_directory)

    @property
    def data_dir(self):
        """ Ysytem user static data storage. """
        return Path(self.data_directory)

    @property
    def repo_data_dir(self):
        """ Repository static data storage. """
        return Path(self.repo_dir) / 'data'

"""
This particular config object is special and doesn't need an explicit
registration. We use the config_dir value to find a sequence of dirs to
load if neccesary, so it has to be handled separately from more standard
config objects.
"""
