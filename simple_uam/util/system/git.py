import shutil
from datetime import datetime
from pathlib import Path, WindowsPath
from typing import Union, List, Optional
from zipfile import ZipFile
import subprocess
import tempfile
import textwrap
import shutil
from urllib.parse import urlparse
import re
from typing import Optional, Union, Dict, List

from .backup import archive_files, backup_file
from ..logging import get_logger

log = get_logger(__name__)

class Git():
    """
    Static class used to wrap a bunch of git commands.
    """

    @staticmethod
    def get_remote_url(
            repo_root : Union[str, Path],
            remote_name : str = "origin",
    ):
        """
        Gets the remote repo for a repository at a particular location.
        Raises error if no git repo exists at location or remote isn't found.

        Uses the command: "git remote get-url <remote_name>"

        WARNING: Not Yet Implemented

        Arguments:
          repo_root : The root directory of the repo.
          remote_name : The remote repo to get the url for (Default: "origin")
        """

        repo_root = Path(repo_root).resolve()

        if not repo_root.exists():
            raise RuntimeError("Could not find git repo at {str(repo_root)}")

        # Finish implementing this, there are enough quirks to this that
        # we should look at it separately.
        raise NotImplementedError()

    @staticmethod
    def config( options : Dict,
                repo_dir : Union[None, str,Path],
    ):
        """
        Sets git configuration options for the global system or a single
        repository.

        Arguments:
          options: Pairs from an option name string to an option value.
          repo_dir: The repository to set local options for, options are set
            globally if None.
        """

        cwd = Path.cwd()
        env_flag = "--global"

        if repo_dir:
           env_flag = "--local"
           repo_dir = Path(repo_dir)
           cwd = repo_dir

        git_cmd = ["git","config", env_flag]

        for opt, val in options.items():
            proc=subprocess.run(
                [*git_cmd, opt, val],
                cwd = cwd,
            )
            proc.check_returncode()

    @staticmethod
    def clone_or_pull(
            repo_uri : str,
            deploy_dir : Union[str,Path],
            branch : Optional[str] = None,
            repo_name : Optional[str] = None,
            remote_name : Optional[str] = None,
            run_clone : bool = True,
            run_pull  : bool = True,
            recursive : bool = True,
            is_submodule : bool = False,
            password_prompt : bool = False,
            password_warning : bool = True,
            remote_user : Optional[str] = None,
            remote_pass : Optional[str] = None,
            quiet : bool = False,
            progress : bool = True,
            verbose : bool = False,
            mkdir : bool = False,
    ):
        """
        Central function that will run a git init/update operation.

        Arguments:
            repo_uri: The url of the core repo.
            deploy_dir: Directory that the repo should be unpacked into.
            branch: The branch we want to checkout or pull from.
            repo_name: Human readable repo name.
            remote_name: Human readable rempte name.
            run_clone: Should we clone a repo if none exists? (init if submodule)
            run_pull: Should we pull a repo if it already exists? (update if submodule)
            recursive: Should we recursively update/init submodules?
            is_submodule: Is this a submodule we're working with?
            password_prompt: Should we ask for a password if none is provided?
            password_warning: Should we warn the user if we're using a password
               on a clone?
            remote_user: The remote user.
            remote_pass: The remote user's password.
            quiet: Run silently. Implies `not password_prompt`.
            progress: Display a progress meter.
            verbose: verbose git output if possible.
            mkdir: create the parent directory of the repo if needed.
        """

        ### Param Init ###

        repo_uri = urlparse(repo_uri)

        co_cmd = None

        if not remote_name:
            remote_name = repo_uri.netloc
        if not repo_name:
            repo_name = repo_uri.path

        remote_user = remote_user or repo_uri.username
        remote_pass = remote_pass or repo_uri.password

        password_prompt = password_prompt and quiet

        deploy_dir = Path(deploy_dir)
        work_dir = deploy_dir.parent # working dir for clone operations
        target_dir = deploy_dir.name # target dir for clone operations

        if mkdir:
            work_dir.mkdir(parents=True, exist_ok=True)

        is_clone_op = not deploy_dir.exists() # is this a clone-style or pull-style op?

        opts = dict(
            repo_uri = repo_uri,
            remote_name = remote_name,
            remote_user = remote_user,
            remote_pass = remote_pass is not None,
            repo_name = repo_name,
            password_prompt = password_prompt,
            deploy_dir = str(deploy_dir),
            branch=branch,
            is_clone_op = is_clone_op,
            recursive=recursive,
            quiet=quiet,
            progress = progress,
            rui_user = repo_uri.username,
            rui_pass = repo_uri.password,
        )

        ### Select Cmd ###

        git_cmd = ['git']
        op_name = "Cloning"
        err = RuntimeError("Invalid git op.")

        if is_clone_op:
            if not run_clone or is_submodule:
                log.exception(
                    "Cannot run pull or submodule op without existing deploy dir.",
                    err = err,
                    **opts,
                )
                raise err
            else:
                op_name = "Cloning"
                git_cmd.append("clone")
                if recursive: git_cmd.append("--recurse-submodules")
                # if branch:
                #     git_cmd.append("--branch")
                #     git_cmd.append(branch)
                if branch:
                    co_cmd = ['git','checkout',branch]
        else:
            if not is_submodule and run_pull:
                op_name = "Pulling"
                git_cmd.append("fetch")
                git_cmd.append("--all")
                if recursive: git_cmd.append("--recurse-submodules")
                if branch:
                    co_cmd = ['git','checkout',branch]
            elif is_submodule:
                op_name = "Updating Submodule"
                git_cmd.append("submodule")
                git_cmd.append("update")
                git_cmd.append("--init")
                if recursive: git_cmd.append("--recursive")
                if branch:
                    co_cmd = ['git','set-branch','--branch',branch]
            else:
                log.exception(
                    "Cannot clone when deploy directory exists.",
                    err = err,
                    **opts,
                )
                raise err

        if quiet: git_cmd.append("--quiet")
        if progress: git_cmd.append("--progress")
        if verbose: git_cmd.append("--verbose")

        ### Prompt for password ###

        def has_pass():
            return remote_user and remote_pass

        password_prompt = password_prompt and is_clone_op

        if password_prompt and not has_pass():
            choice = input(textwrap.dedent(
                f"""
                {op_Name} for repo at {str(deploy_dir)}.

                Server: {remote_name}
                Repo: {repo_name}
                Full URL: {repo_url.geturl()}

                Repo not found, how would you like to authenticate:

                   1) Automatically via SSH, or because no authentication is
                      needed.
                   2) With a username and password.

                Please enter your choice (1 or 2):
                """
            ))

            if choice == '1':
                pass
            elif choice != '2':
                err = RuntimeError("Please enter a valid choice.")
                log.exception(
                    "Please enter a valid choice.",
                    err = err,
                    **opts,
                )
                raise err
            else:
                remote_user = input(f"Enter Username for {remote_name}: ")
                remote_pass = input(f"Enter Password for {remote_name}: ")

        ### Validate Password Entry ###

        if is_clone_op and has_pass():
            log.warning(textwrap.dedent(
                f"""
                A plaintext password has been provided for a clone operation.
                Git will save this locally within the remote, this is insecure.
                Please consider installing an SSH key for {remote_name} instead.
                """
            ))
            choice = input("Are you sure you want to continue? (y/N)")
            if choice == "N":
                raise RuntimeError("Confirmation not given, aborting operation.")
            elif choice != "y":
                raise RuntimeError("Invalid confirmation, aborting operation.")

        ## Fix up the uri if we have a username and password.

        if has_pass():
            repo_uri = repo_uri._replace(
                netloc=f"{remote_user}:{remote_pass}@{repo_uri.hostname}"
            )

        ### Run the command ###

        if is_clone_op:
            proc=subprocess.run(
                [*git_cmd, repo_uri.geturl(), target_dir],
                cwd = work_dir,
            )
            proc.check_returncode()
        else:
            proc = subprocess.run(
                git_cmd,
                cwd = deploy_dir,
            )
            proc.check_returncode()

        if co_cmd: # Checkout a particular branch after fetch or submod
            proc = subprocess.run(
                co_cmd,
                cwd = deploy_dir,
            )
            proc.check_returncode()
