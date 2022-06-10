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
def creoson_server(ctx):
    """
    Downloads the creoson server files to cache.
    """
    pass

@task
def direct2cad(ctx):
    """
    Downloads the direct2cad repository to cache.
    """
    pass

@task(mkdirs, creoson_server, direct2cad)
def setup_reference(ctx):
    """
    Will set up the reference directory if needed.

    Note: Will delete the contents of the reference directory!
    """
    manager.setup_ref_dir(
        direct2cad_repo=...,
        creoson_server_zip=...,
    )
