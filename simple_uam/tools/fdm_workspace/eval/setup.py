"""
Various setup and development tasks for SimpleUAM Utility Modules.
"""

import shutil
from simple_uam.util.invoke import task, call
from simple_uam.util.config import Config, PathConfig, \
    AuthConfig, CorpusConfig, FDMEvalConfig
from simple_uam.util.logging import get_logger
from simple_uam.util.system import Git
from simple_uam.util.system.windows import download_file

from simple_uam.fdm.eval.manager import FDMEvalManager
from simple_uam.fdm.eval.session import FDMEvalSession
from simple_uam.fdm.eval.workspace import FDMEvalWorkspace
from pathlib import Path
import textwrap
import sys

import subprocess

log = get_logger(__name__)
manager = FDMEvalManager()

@task
def mkdirs(ctx):
    """
    Creates the various directories needed for managing direct2cad workspaces.
    """

    log.info(
        "Initializing workspace directory structure."
    )
    manager.init_dirs()


fdm_env_dir = Path(Config[FDMEvalConfig].cache_dir) / 'fdm_env'
fdm_env_repo = Config[CorpusConfig].fdm_eval.repo
fdm_env_branch = Config[CorpusConfig].fdm_eval.branch

@task
def fdm_env(ctx,  prompt=True, quiet=False, verbose=False):
    """
    Clones the fdm environment repo into the appropriate cache folder.
    Required to setup fdm_env reference dir.

    Arguments:
      prompt: Prompt for a password on initial git clone.
      quiet: Run in quiet mode.
      verbose: Run in verbose mode.
    """

    git_args = dict(
        repo_uri = fdm_env_repo,
        deploy_dir = str(fdm_env_dir),
        branch = fdm_env_branch,
        remote_user = Config[AuthConfig].isis_user,
        remote_pass = Config[AuthConfig].isis_token,
        password_prompt = prompt,
        quiet = quiet,
        verbose = verbose,
        mkdir = True
    )

    if not quiet:
        log.info("Running git clone/pull for uam_fdm_env."
                 ,**git_args)

    Git.clone_or_pull(**git_args)

@task(mkdirs, fdm_env)
def setup_reference(ctx):
    """
    Will set up the reference directory if needed.

    Note: Will delete the contents of the reference directory!
    """

    log.info(
        "Settting up FDM evaluation environment reference directory.",
        fdm_env_repo=str(fdm_env_dir),
    )

    manager.setup_reference_dir(
        fdm_env_repo=fdm_env_dir,
    )