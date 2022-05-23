from .config import UAMWorkspaceConfig
from .generic.config import RecordsConfig, WorkspaceConfig
from util.config import Config, PathConfig, OmegaConf
import util.paths as paths
from typing import List
from pathlib import Path
from util.logging import get_logger

log = get_logger(__name__)

module_dir : Path = paths.repo_dir / 'uam-workspace'
""" Dir for this module's source """

external_deps_dir : Path = module_dir / 'external'
""" Dir for git submodules w/ external data """
