"""Wrapper that provides accessor functions for app data directories"""

from pathlib import Path
from util.config import Config, PathConfig

repo_dir = Path(__file__).resolve().parent.parent.parent.parent.parent

config_dir = Path(Config[PathConfig].config_dir)

data_dir = Path(Config[PathConfig].data_dir)

cache_dir = Path(Config[PathConfig].cache_dir)

log_dir = Path(Config[PathConfig].log_dir)

documents_dir = Path(Config[PathConfig].documents_dir)

work_dir = Path(Config[PathConfig].work_dir)
