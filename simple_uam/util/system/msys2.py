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
import json
import importlib.resources as resources
from typing import Optional, Union, List, Dict
from attrs import define, field

from .backup import archive_files
from ..logging import get_logger

log = get_logger(__name__)

@define
class Msys2CompletedProcess():

    args : List = field()

    flag_output : Dict = field()

    @property
    def returncode(self):
        if 'completed' in self.flag_output:
            return self.flag_output['completed']
        else:
            return None

    def check_returncode(self):
        if self.returncode == None:
            self.raise_errors()
        elif self.returncode != 0:
            raise subprocess.CalledProcessError(
                cmd = " ".join(self.args),
                stdout = self.stdout,
                stderr = self.stderr,
            )

    @property
    def error(self):
        if 'error' in self.flag_output:
            return {self.flag_output['error']: self.flag_output.get('message')}
        else:
            return None

    def raise_errors(self):
        if self.error:
            raise RuntimeError(
                f"Msys2.run() existed with error `{self.error}`")

    text : bool = field(
        default = False
    )

    stdout_file : Optional[Path] = field(
        default=None
    )

    stdout_data : Union[None, str, bytes] = field(
        default = None
    )

    @property
    def stdout(self):
        self.load_stdout()
        return self.stdout_data

    def load_stdout():
        if self.stdout_data:
            pass
        elif self.stdout_file and self.text:
            self.stdout_data = self.stdout_file.read_text()
        elif self.stdout_file:
            self.stdout_data = self.stdout_file.read_bytes()

    stderr_file : Optional[Path] = field(
        default = None
    )

    stderr_data : Union[None, str, bytes] = field(
        default = None
    )

    @property
    def stderr(self):
        self.load_stderr()
        return self.stderr_data

    def load_stderr(self):
        if self.stderr_data:
            pass
        elif self.stderr_file and self.text:
            self.stderr_data = self.stderr_file.read_text()
        elif self.stderr_file:
            self.stderr_data = self.stderr_file.read_bytes()


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
            stdout=True,
            stderr=True,
            text=True,
        )

    @staticmethod
    def run( args : Union[str,Path,List[Union[str,Path]]],
             cwd : Union[None, str, Path] = None,
             stdin : Union[None,str, bytes] = None,
             stdout : Union[bool, str, Path] = False,
             stderr : Union[bool, str, Path] = False,
             timeout : Optional[int] = None,
             reraise_errors : bool = True,
             text : bool = False,
             poll_interval : int = 1,
             data_dir : Union[None, str, Path] = False,
    ):
        """
        Akin to `subprocess.run` but will run the command within the local
        msys2 environment. Uses a shim to allow waiting on a command to
        finish even when the msys terminal detaches.

        Arguments:
          args: A list of strings and Paths to serve as the command and args to
            be run. Note that Path objects are automatically converted to the
            appropriate cygwin paths.
          cwd: The directory in which to run the command, if provided must
            be provided as a Path object.(Default: cwd)
          stdin: The data to be sent to the process via STDIN. If
            text is true this should be a str, otherwise a bytes object.
            (Default: None)
          stdout: Should be save the stdout from the process? If True, will
            be in the returned Msys2CompletedProcess object; If a string or
            Path it will be placed in the appropriate file; otherwise will
            be ignored. (Default: False)
          stderr: Should be save the stderr from the process? If True, will
            be in the returned Msys2CompletedProcess object; If a string or
            Path it will be placed in the appropriate file; otherwise will
            be ignored. (Default: False)
          timeout: How long should we wait until we give up on the process
            and raise an error (Default: None)
          reraise_errors: Should we try to re-raise errors from the shim in
            this process? (Default: True)
          text: Should stdin, stdout, and stderr use strings (as opposed to
            bytes objects?) (Default: False)
          poll_interval: How often should we poll for process completion?
            (Default: 1)
          data_dir: Should we store all the intermediate files in a
            non-temporary dir? If so, where? (Default: None)
        """

        # Ensure arguments are in list form
        if not isinstance(args, list):
            args = [args]

        # The data we'll write into a file for the shim to read.
        shim_data = dict()

        # Format the args
        shim_args = list()

        for arg in args:
            shim_arg = arg
            if isinstance(arg, str):
                shim_arg = {'str': arg}
            elif isinstance(arg, Path):
                shim_arg = {'path': str(Path(arg).resolve())}
            else:
                raise RuntimeError(
                    f"Argument of type `{type(arg).__name__}` not allowed in "
                    f"Msys2.run()'s args parameter. The argument '{arg}' in "
                    f"argument list '{args}' is invalid."
                )
            shim_args.append(shim_arg)

        shim_data['args'] = shim_args

        # The current working dir
        if not cwd:
            cwd = Path.cwd()
        cwd = Path(cwd).resolve()
        shim_data['cwd'] = str(cwd)

        # Working with files now so we enter a tempdir
        with tempfile.TemporaryDirectory(prefix="Msys2Run") as temp_dir:

            if data_dir:
                temp_dir = data_dir

            temp_dir = Path(temp_dir).resolve()

            std_ext = '.txt' if text else '.bin'

            if stdin:
                stdin_file = (temp_dir / 'stdin').with_suffix(std_ext).resolve()
                if text:
                    stdin_file.write_text(stdin)
                else:
                    stdin_file.write_bytes(stdin)
                shim_data['stdin'] = str(stdin_file)

            stdout_file = None
            if stdout:
                if isinstance(stdout,bool):
                    stdout_file = (temp_dir / 'stdout').with_suffix(std_ext).resolve()
                else:
                    stdout_file = Path(stdout).resolve()
                shim_data['stdout'] = str(stdout_file)

            stderr_file = None
            if stderr:
                if isinstance(stderr,bool):
                    stderr_file = (temp_dir / 'stderr').with_suffix(std_ext).resolve()
                else:
                    stderr_file = Path(stderr).resolve()
                shim_data['stderr'] = str(stderr_file)

            if timeout:
                shim_data['timeout'] = timeout

            flag_file = (temp_dir / 'shim_flag.json').resolve()
            shim_data['stop_flag'] = str(flag_file)

            data_file = (temp_dir / 'shim_data.json').resolve()
            with data_file.open('w') as fp:
                json.dump(shim_data,fp,indent=2)

            log.info(
                "Wrote Msys2 shim data file.",
                file=str(data_file),
                temp_dir=str(temp_dir),
                flag_file=str(flag_file),
                data_file=str(data_file),
                **shim_data,
            )

            # Actually run the shim now that we've created the files
            flag_output = Msys2._run_shim(
                data_file=data_file,
                flag_file=flag_file,
                timeout=timeout,
                poll_interval=poll_interval,
            )

            # Make the results neater for the the user.
            process = Msys2CompletedProcess(
                args = args,
                flag_output = flag_output,
                text=text,
                stdout_file=stdout_file,
                stderr_file=stderr_file,
            )

            if isinstance(stdout,bool): process.load_stdout()
            if isinstance(stderr,bool): process.load_stderr()
            if reraise_errors: process.raise_errors()

            return process

    @staticmethod
    def bindir():
        """
        Gets the default binary directory for msys2, assumes that it is
        in a specific place relative to `msys2.exe`.
        """

        exe = Path(shutil.which('msys2.exe')).resolve()
        root_dir = exe.parent
        bin_dir = root_dir / 'usr' / 'bin'

        return bin_dir

    @staticmethod
    def _run_shim(data_file : Path,
                  flag_file : Path,
                  timeout : Optional[int],
                  poll_interval : int):
        """
        Helper that runs the shim with the target data_file, and waits on the
        flag file to appear.

        Arguments:
          data_file: the path of the data to be run
          flag_file: path to file where flag will appear
          **kwargs: See similar args in run
        """

        if flag_file.exists():
            raise RuntimeError(
                f"Cannot use msys2 cmd shim for {str(flag_file)} because it "
                "already exists.")

        with resources.path('simple_uam.data.fdm','msys2_shim.py') as shim:

            shim_file = Path(shim).resolve()
            process_cmd = [
                'msys2.exe',
                'python',
                shim_file,
                data_file,
                "--log-level=DEBUG",
                "--wait",
            ]

            log.info(
                "Running Msys2 shim with command:",
                cmd=process_cmd,
            )
            process = subprocess.run(process_cmd)

            elapsed = 0

            if timeout == None:
                log.info(
                    "No Msys timeout provided. Waiting indefinitely."
                )

            while (timeout == None) or (elapsed <= timeout):

                log.info(
                    "Checking for existence of output flag file.",
                    timeout=timeout,
                    elapsed=elapsed,
                    poll_interval=poll_interval,
                    exists=flag_file.exists(),
                )

                if flag_file.exists():
                    with flag_file.open('r') as fp:
                        return json.load(fp)
                time.sleep(poll_interval)
                elapsed += poll_interval

            raise RuntimeError(
                f"Running msys2 cmd shim (at `{str(shim_file)}`) with "
                f"{str(data_file)} did not produce an output at "
                f"{str(flag_file)} within the alloted timeout."
            )
