"""
Module w/ functions and tasks for manipulating the reference copy of the
workspace.
"""

from .config import UAMWorkspaceConfig
from util.config import Config
from .paths import *
from typing import List
from pathlib import Path
from util.logging import get_logger
from util.invoke import task
import subprocess

log = get_logger(__name__)

swri_subdirs : List[str] = [
    'creoson_server',
    'uam_direct2cad',
]
""" The git submodules (in external_deps_dir) we need from swri. """

@task
def init_swri_repos(ctx, no_init = False, no_update = False):
    """
    Initializes and updates the swri project repos from git.isis.vanderbilt.edu
    within the `<repo-root>/uam-workspace/external/` directory.

    Arguments:
      no_init: Skip running `git submodule init` step.
      no_update: Skip running `git submodule update` step.
    """

    for swri_subdir in swri_subdirs:
        swri_dir : Path = external_deps_dir / swri_subdir

        if not no_init:
            log.info(
                "Running `git submodule init`.",
                repo_dir=str(swri_dir),
            )
            subprocess.run(
                ['git', 'submodule', 'init'],
                cwd=swri_dir,
            )

        if not no_update:
            log.info(
                "Running `git submodule update`.",
                repo_dir=str(swri_dir),
            )
            subprocess.run(
                ['git', 'submodule', 'update'],
                cwd=swri_dir,
            )

@task
def setup_workspace(ctx):
    """
    Setup the reference workspace in reference_dir
    """

    raise
