"""
Various setup and development tasks for SimpleUAM Utility Modules.
"""

import shutil
from simple_uam.util.invoke import task, call
from simple_uam.util.config import Config, PathConfig, FDMCompileConfig, \
    AuthConfig, CorpusConfig
from simple_uam.util.logging import get_logger
from simple_uam.util.system import Git
from simple_uam.util.system.windows import download_file

from simple_uam.fdm.compile.manager import FDMCompileManager
from pathlib import Path
import textwrap
import sys

import subprocess

log = get_logger(__name__)
manager = FDMCompileManager()

@task
def mkdirs(ctx):
    """
    Creates the various directories needed for managing direct2cad workspaces.
    """

    log.info(
        "Initializing workspace directory structure."
    )
    manager.init_dirs()

fdm_compile_dir = Path(Config[FDMCompileConfig].cache_dir) / 'fdm_compile'
fdm_compile_repo = Config[CorpusConfig].fdm_compile.repo
fdm_compile_branch = Config[CorpusConfig].fdm_compile.branch

@task
def flight_dynamics_model(ctx,  prompt=True, quiet=False, verbose=False):
    """
    Clones the flight dynamics model rep into the appropriate cache folder.
    Required to setup fdm_compile reference dir.

    Arguments:
      prompt: Prompt for a password on initial git clone.
      quiet: Run in quiet mode.
      verbose: Run in verbose mode.
    """

    git_args = dict(
        repo_uri = fdm_compile_repo,
        deploy_dir = str(fdm_compile_dir),
        branch = fdm_compile_branch,
        remote_user = Config[AuthConfig].isis_user,
        remote_pass = Config[AuthConfig].isis_token,
        password_prompt = prompt,
        quiet = quiet,
        verbose = verbose,
        mkdir = True
    )

    if not quiet:
        log.info("Running git clone/pull for the flight model."
                 ,**git_args)

    Git.clone_or_pull(**git_args)

@task(mkdirs, flight_dynamics_model)
def setup_reference(ctx):
    """
    Will set up the reference directory if needed.

    Note: Will delete the contents of the reference directory!
    """

    log.info(
        "Settting up fdm_compile workspace reference directory.",
        fdm_compile_repo=str(fdm_compile_dir),
    )

    manager.setup_reference_dir(
        fdm_src_repo=fdm_compile_dir,
    )
