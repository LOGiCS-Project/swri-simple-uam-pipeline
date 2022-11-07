import shutil
from datetime import datetime
from pathlib import Path, WindowsPath
from typing import Union, List, Optional
from zipfile import ZipFile
import subprocess
import tempfile
import textwrap
from urllib.parse import urlparse
import re
import time
import shutil
import shlex
import json
from contextlib import ExitStack, contextmanager
import importlib.resources as resources
from typing import Optional, Union, List, Dict, Callable, Any
from attrs import define, field
from pathlib import Path
from .backup import archive_files, backup_file
from ..logging import get_logger

log = get_logger(__name__)

class Msys2():
    """
    Static class used to wrap a bunch of msys2 commands.
    """

    @staticmethod
    def install(*packages : List[str]):
        """
        Installs a bunch of msys2 packages to the local environment.
        If packages already exist, will only update needed ones.

        Arguments:
          packages: The list of packages to install or update.
        """

        pacman_cmd = ['pacman','-Su','--needed','--noconfirm', *packages]

        Msys2.run(
            pacman_cmd,
            cwd=Path.cwd(),
        )

    _root = None

    @staticmethod
    def root():
        """
        The root msysy 2 directory, the dir containing 'msys2.exe'.
        """
        if Msys2._root == None:
            Msys2._root = Path(shutil.which('msys2.exe')).resolve().parent
        return Msys2._root

    @staticmethod
    def bin_root():
        """
        Gets the default binary directory for msys2, assumes that it is
        in a specific place relative to `msys2.exe`.
        """
        return (Msys2.root() / 'usr' / 'bin').resolve()

    @staticmethod
    def bash_path():
        """
        The path to the bash executable used for an msys2 login shell.
        """
        return  (Msys2.bin_root() / 'bash.exe').resolve()

    @staticmethod
    def tmp_root():
        """
        The msys2 temp directory, should be on the same drive as the msys2
        install bypassing some issues with paths.
        """
        return (Msys2.root() / 'tmp').resolve()

    @staticmethod
    @contextmanager
    def tempdir(suffix=None, prefix=None, ignore_cleanup_errors=False):
        """
        Creates and returns temporary directory on the same drive as the
        msys2 binary.

        Arguments: Same as tempfile.TemporaryDirectory except without 'dir'.
        """

        Msys2.tmp_root().mkdir(parents=True, exist_ok=True)

        with tempfile.TemporaryDirectory(
                suffix=suffix,
                prefix=prefix,
                dir=Msys2.tmp_root(),
                ignore_cleanup_errors=ignore_cleanup_errors) as temp_dir:
            yield temp_dir

    @staticmethod
    def cygpath_path():
        """
        The path to the cygpath executable for converting windowspaths to
        cygwin paths.
        """
        return  (Msys2.bin_root() / 'cygpath.exe').resolve()

    @staticmethod
    def cygpath(path : Union[Any,Path],
                passthrough : bool = False,
                resolve : bool = False,
                cwd : Union[None,str,Path] = False,
                run_cmd : Optional[Callable] = None):
        """
        Will convert a windows path to a valid cygwin path.

        Arguments:
          path: The path to covert to a cygwin path
          passthrough: Should we allow non-path ojects to pass through
            unchanged. If False non-path or str objects raise an error and
            strs are converted to paths. If true all non-Path objects,
            including strings are returned without change. (Default: False)
          resolve: Should all relative paths be converted into absolute paths
            (Default: False)
          cwd: The working directory to be used if resolve is true.
            (Default: cwd)
          run_cmd: A command with a signature equal to subprocess.run, that
            will be used to actual evaluate the function in the location.
            (Default: subprocess.run)
        """

        if passthrough and not isinstance(path, Path):
            return path

        path = Path(path)

        if not cwd:
            cwd = Path.cwd()
        cwd = Path(cwd).resolve()

        if resolve and not path.is_absolute():
            path = (cwd / path).resolve()

        if not run_cmd:
            run_cmd = subprocess.run

        log.info(
            f"Converting path win_path to cygwin form using cygpath.",
            win_path = str(path),
            cwd = str(cwd),
            resolve = resolve,
            run_cmd_module=run_cmd.__module__,
            run_cmd_name=run_cmd.__name__,
        )

        process = run_cmd(
            [Msys2.cygpath_path(),"-u",path],
            capture_output=True,
            text=True,
        )

        process.check_returncode()

        out_path = process.stdout.strip()

        log.debug(
            f"Finished converting path to cygwin form.",
            win_path = str(path),
            out_path = str(out_path),
            cwd = str(cwd),
            resolve = resolve,
            run_cmd_module=run_cmd.__module__,
            run_cmd_name=run_cmd.__name__,
        )

        return out_path



    @staticmethod
    def run( args : Union[str,Path,List[Union[str,Path]]],
             cwd : Union[str,Path],
             *,
             run_cmd : Optional[Callable] = None,
             **kwargs,
    ):
        """
        Akin to `subprocess.run` but will run the command within the local
        msys2 environment. Calls msys bash directly.

        Arguments:
          args: A list of strings and Paths to serve as the command and args to
            be run. Note that Path objects are automatically converted to the
            appropriate cygwin paths.
          cwd: The working directory for the command to be run in, note this
            is mandatory because it needs to be passed to bash explicitle.
          run_cmd: A command with a signature equal to subprocess.run, that
            will be used to actual evaluate the function in the location.
            (Default: subprocess.run)
          **kwargs: Other args to be passed through to the underlying
            run_cmd.
        """

        msys_bash = Msys2.bash_path()

        cwd = Path(cwd)

        # Normalize various arguments
        if not run_cmd:
            run_cmd = subprocess.run

        if not isinstance(args, list):
            args = [args]

        def norm_arg(a):
            return str(Msys2.cygpath(
                path=a,
                passthrough=True,
                cwd=cwd,
                resolve=False,
                run_cmd=run_cmd,
            ))

        cd_args = ['cd', norm_arg(cwd)]

        log.info(
            "Generated msys2 command arg lists.",
            cmd_args = args,
            cd_args  = cd_args,
        )

        cmd_str = shlex.join([norm_arg(a) for a in args])
        cd_str  = shlex.join(cd_args)

        cmd = f"{cd_str} ; {cmd_str}"

        log.info(
            "Generated msys2 command arg string.",
            cmd_str = cmd_str,
            cd_str = cd_str,
            cmd = cmd,
        )

        bash_cmd = [
            msys_bash,
            '-l',             # run a login shell
            '-c',             # run a command
            cmd, # command string to run
        ]


        log.info(
            "Running Msys2 command via bash.",
            args = [str(a) for a in bash_cmd],
            cwd = str(cwd),
            run_cmd_module=run_cmd.__module__,
            run_cmd_name=run_cmd.__name__,
            **kwargs,
        )

        return run_cmd(
            bash_cmd,
            cwd=cwd,
            **kwargs,
        )
