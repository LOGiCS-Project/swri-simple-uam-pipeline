"""
Various setup and development tasks for SimpleUAM Utility Modules.
"""

import shutil
from simple_uam.util.invoke import task, call
from simple_uam.util.config import Config, PathConfig, WinSetupConfig
from simple_uam.util.logging import get_logger

from simple_uam.d2c_workspace.manager import D2CManager
from simple_uam.d2c_workspace.session import D2CSession
from simple_uam.d2c_workspace.workspace import D2CWorkspace

import subprocess

log = get_logger(__name__)
manager = D2CManager()

@task
def mkdirs(ctx):
    """
    Creates the various directories needed for managing direct2cad workspaces.
    """

    manager.init_dirs()

@task
def delete_locks(ctx,
                 skip_reference=False,
                 skip_records=False):
    """
    Forcefully deletes all the locks for direct2cad workspaces.
    Only use this when no workspaces are operational, otherwise sessions in a
    workspace can clobber each other.

    Arguments:
        skip_reference: If true, skip deleting the reference lockfile.
        skip_records: If true, skip deleting the records lock.
    """

    manager.delete_locks(
        skip_reference=skip_reference,
        skip_records=skip_records,
    )

@task
def prune_records(ctx):
    """
    Deletes the oldest files in the records dir if there are too many.
    """
    manager.prune_records()

@task(mkdirs)
def setup_reference(ctx):
    """
    Will set up the reference directory if needed.

    Note: Will delete the contents of the reference directory!
    """
    manager.setup_ref_dir()
