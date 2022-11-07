"""
Various setup and development tasks for SimpleUAM Utility Modules.
"""

import shutil
from simple_uam.util.invoke import task, call
from simple_uam.util.config import Config, PathConfig, D2CWorkspaceConfig, \
    AuthConfig, CorpusConfig
from simple_uam.util.logging import get_logger
from simple_uam.util.system import Git
from simple_uam.util.system.windows import download_file

from simple_uam.direct2cad.manager import D2CManager
from simple_uam.direct2cad.session import D2CSession
from simple_uam.direct2cad.workspace import D2CWorkspace
import importlib.resources as resources
from pathlib import Path
import textwrap
import sys

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
creoson_server_api_endpoint = Config[CorpusConfig].creoson_server.api
creoson_server_manual_uri = Config[CorpusConfig].creoson_server.manual
# creoson_server_repo = "https://git.isis.vanderbilt.edu/SwRI/creoson/creoson-server.git"
# creoson_server_branch = 'dchee-jars'
creoson_server_zip = creoson_server_dir / "CreosonServerWithSetup-2.8.0-win64.zip"
sys_input = input

@task
def creoson_server(ctx,
                   input=None,
                   download=False,
                   manual=False):
    """
    Downloads the creoson server zip.
    Required to setup direct2cad reference dir.

    Arguments:
      input: Location of server zip provided manually.
      download: Force download of server zip iff Isis credentials are available.
      manual: Force manual download instead of automatic.
    """

    creoson_server_dir.mkdir(parents=True, exist_ok=True)

    if input:

        input = Path(input)

        if creoson_server_zip.exists():
            log.warning(
                "Found pre-existing creoson server zip when user has provided manual input, deleting.",
                output=str(creoson_server_zip),
            )

            creoson_server_zip.unlink()

        log.info(
            "User provided creoson server zip manually, moving to install loc.",
            input=str(input),
            output=str(creoson_server_zip),
        )

        shutil.copy2(input, creoson_server_zip)

    elif creoson_server_zip.exists() and not (download or manual):

        log.info(
            "Creoson server zip already exists, skipping download.",
            output=str(creoson_server_zip),
        )

    elif Config[AuthConfig].isis_auth and not manual:

        log.info(
            "Isis credentials found, download creoson server through API endpoint.",
            output=creoson_server_zip,
        )

        download_file(
            uri=creoson_server_api_endpoint,
            output=creoson_server_zip,
            params=dict(private_token=Config[AuthConfig].isis_token),
        )

    else:

        log.info(
            "No Isis credentials found, using manual download."
        )

        print(textwrap.dedent(
            f"""
            Please Download the Creoson Server Zip manually:

              From: {creoson_server_manual_uri}

              To: {str(creoson_server_zip.resolve())}

            Press enter when completed:
            """
        ))
        sys.stdin.readline()

        if not creoson_server_zip.exists():
            err = RuntimeError("No Server Zip Found.")
            log.exception(
                textwrap.dedent(
                    f"""
                    Server was not placed in correct location.
                    Try downloading again and using the '--input' flag
                    to copy the file into the install location. E.g.:

                    > pdm run d2c-workspace setup.creoson-server --input=C:/file/is/here.zip
                    """,
                ),
                err=err,
                output=str(creoson_server_zip),
            )
            raise err

    # git_args = dict(
    #     repo_uri = creoson_server_repo,
    #     deploy_dir = str(creoson_server_dir),
    #     remote_user = Config[AuthConfig].isis_user,
    #     remote_pass = Config[AuthConfig].isis_token,
    #     branch = creoson_server_branch,
    #     password_prompt = prompt,
    #     quiet = quiet,
    #     verbose = verbose,
    #     mkdir = True
    # )

    # if not quiet:
    #     log.info("Running git clone/pull for creoson server zip."
    #              ,**git_args)

    # Git.clone_or_pull(**git_args)

direct2cad_dir = Path(Config[D2CWorkspaceConfig].cache_dir) / 'direct2cad'
direct2cad_repo = Config[CorpusConfig].direct2cad.repo
direct2cad_branch = Config[CorpusConfig].direct2cad.branch

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
        remote_user = Config[AuthConfig].isis_user,
        remote_pass = Config[AuthConfig].isis_token,
        password_prompt = prompt,
        quiet = quiet,
        verbose = verbose,
        mkdir = True
    )

    if not quiet:
        log.info("Running git clone/pull for uam_direct2cad."
                 ,**git_args)

    Git.clone_or_pull(**git_args)

uav_workflows_dir = Path(Config[D2CWorkspaceConfig].cache_dir) / 'uav_workflows'
uav_workflows_repo = Config[CorpusConfig].uav_workflows.repo
uav_workflows_branch = Config[CorpusConfig].uav_workflows.branch

@task
def uav_workflows(ctx,  prompt=True, quiet=False, verbose=False):
    """
    Clones the creoson server repo into the appropriate cache folder.
    Required to setup uav_workflows reference dir.

    Arguments:
      prompt: Prompt for a password on initial git clone.
      quiet: Run in quiet mode.
      verbose: Run in verbose mode.
    """

    git_args = dict(
        repo_uri = uav_workflows_repo,
        deploy_dir = str(uav_workflows_dir),
        branch = uav_workflows_branch,
        remote_user = Config[AuthConfig].isis_user,
        remote_pass = Config[AuthConfig].isis_token,
        password_prompt = prompt,
        quiet = quiet,
        verbose = verbose,
        mkdir = True
    )

    if not quiet:
        log.info("Running git clone/pull for uav_workflows."
                 ,**git_args)

    Git.clone_or_pull(**git_args)

@task(mkdirs, creoson_server, direct2cad, uav_workflows)
def setup_reference(ctx, creoson_gui = False):
    """
    Will set up the reference directory if needed.

    Note: Will delete the contents of the reference directory!

    Arguments:
      creoson_gui: Use the creoson_server gui to setup ports instead of just
        copying file from SimpleUAM's data.
    """

    log.info(
        "Settting up d2c workspace reference directory.",
        direct2cad_repo=str(direct2cad_dir),
        creoson_server_zip=str(creoson_server_zip),
        uav_workflows_repo=str(uav_workflows_dir),
    )

    with resources.path('simple_uam.data.creoson','setvars.bat') as setvars_file:

        manager.setup_reference_dir(
            direct2cad_repo=direct2cad_dir,
            uav_workflows_repo=uav_workflows_dir,
            creoson_server_zip=creoson_server_zip,
            setvars_file=None if creoson_gui else setvars_file,
        )
