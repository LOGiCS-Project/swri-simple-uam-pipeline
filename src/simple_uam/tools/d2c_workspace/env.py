"""
Various setup and development tasks for SimpleUAM Utility Modules.
"""

import shutil
from simple_uam.util.invoke import task, call
from simple_uam.util.config import Config, PathConfig, D2CWorkspaceConfig
from simple_uam.util.logging import get_logger

from simple_uam.direct2cad.manager import D2CManager
from simple_uam.direct2cad.session import D2CSession
from simple_uam.direct2cad.workspace import D2CWorkspace
from pathlib import Path

import subprocess

log = get_logger(__name__)
manager = D2CManager()

@task
def mkdirs(ctx):
    """
    Creates the various directories needed for managing direct2cad workspaces.
    """

    log.info(
        "Initializing workspace directory structure."
    )
    manager.init_dirs()

creoson_server_dir = Path(Config[D2CWorkspaceConfig].cache_dir) / 'creoson_server'
creoson_server_repo = "https://git.isis.vanderbilt.edu/SwRI/creoson/creoson-server.git"
creoson_server_branch = 'dchee-jars'
creoson_server_zip = creoson_server_dir / "CreosonServerWithSetup-2.8.0-win64.zip"

@task
def creoson_server(ctx,  prompt=True, quiet=False, verbose=False):
    """
    Clones the creoson server repo into the appropriate cache folder.
    Required to setup direct2cad reference dir.

    Arguments:
      prompt: Prompt for a password on initial git clone.
      quiet: Run in quiet mode.
      verbose: Run in verbose mode.
    """

    git_args = dict(
        repo_uri = creoson_server_repo,
        deploy_dir = str(creoson_server_dir),
        branch = creoson_server_branch,
        password_prompt = prompt,
        quiet = quiet,
        verbose = verbose,
        mkdir = True
    )

    if not quiet:
        log.info("Running git clone/pull for creoson server zip."
                 ,**git_args)

    Git.clone_or_pull(**git_args)

direct2cad_dir = Path(Config[D2CWorkspaceConfig].cache_dir) / 'direct2cad'
direct2cad_repo = "https://git.isis.vanderbilt.edu/SwRI/uam_direct2cad.git"
direct2cad_branch = 'main'

@task
def direct2cad(ctx,  prompt=True, quiet=False, verbose=False):
    """
    Clones the creoson server repo into the appropriate cache folder.
    Required to setup direct2cad reference dir.

    Arguments:
      prompt: Prompt for a password on initial git clone.
      quiet: Run in quiet mode.
      verbose: Run in verbose mode.
    """

    git_args = dict(
        repo_uri = direct2cad_repo,
        deploy_dir = str(direct2cad_dir),
        branch = direct2cad_branch,
        password_prompt = prompt,
        quiet = quiet,
        verbose = verbose,
        mkdir = True
    )

    if not quiet:
        log.info("Running git clone/pull for uam_direct2cad."
                 ,**git_args)

    Git.clone_or_pull(**git_args)

@task(mkdirs, creoson_server, direct2cad)
def setup_reference(ctx):
    """
    Will set up the reference directory if needed.

    Note: Will delete the contents of the reference directory!
    """

    log.info(
        "Settting up d2c workspace reference directory.",
        direct2cad_repo=direct2cad_dir,
        creoson_server_zip=creoson_server_zip,
    )
    manager.setup_ref_dir(
        direct2cad_repo=direct2cad_dir,
        creoson_server_zip=creoson_server_zip,
    )
