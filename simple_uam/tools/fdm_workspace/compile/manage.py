"""
Various setup and development tasks for SimpleUAM Utility Modules.
"""

import shutil
from simple_uam.util.invoke import task, call
from simple_uam.util.config import Config, PathConfig, FDMCompileConfig, \
    AuthConfig, CorpusConfig
from simple_uam.util.logging import get_logger
from simple_uam.fdm.compile.manager import FDMCompileManager
from pathlib import Path
import subprocess

log = get_logger(__name__)

manager = FDMCompileManager()

@task
def delete_locks(ctx,
                 skip_reference=False,
                 skip_results=False):
    """
    Forcefully deletes all the locks for direct2cad workspaces.
    Only use this when no workspaces are operational, otherwise sessions in a
    workspace can clobber each other.

    Arguments:
        skip_reference: If true, skip deleting the reference lockfile.
        skip_results: If true, skip deleting the results lock.
    """

    manager.delete_locks(
        skip_reference=skip_reference,
        skip_results=skip_results,
    )

@task
def prune_results(ctx):
    """
    Deletes the oldest files in the results dir if there are too many.
    """
    manager.prune_results()

@task
def workspaces_dir(ctx):
    """
    Prints the root directory of the workspaces.
    """

    print(str(Path(manager.config.workspaces_dir)))

@task
def cache_dir(ctx):
    """
    Prints the cache directory for these workspaces.
    """

    print(str(Path(manager.config.cache_dir)))

@task
def results_dir(ctx):
    """
    Prints the directory where session results are kept.
    """

    print(str(manager.config.results_path))
