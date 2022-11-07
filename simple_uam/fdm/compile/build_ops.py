
from simple_uam.util.system.msys2 import Msys2
from simple_uam.util.system.text_dir import TDir
from simple_uam.util.config import Config, FDMCompileConfig
from typing import Optional, Union, List, Dict, Callable, Any
import importlib.resources as resources
import subprocess
from pathlib import Path
from simple_uam.util.logging import get_logger
import shutil

log = get_logger(__name__)

def wrap_build_op( args : List[Any],
                   cwd : Union[str,Path],
                   stdout : Union[str,Path],
                   stderr : Union[str,Path],
                   log_dir : Union[None, str, Path] = None,
                   timeout : Optional[int] = None,
                   run_cmd : Optional[Callable] = None,
):
    """
    Does the argument management and normalization for the bunch of build ops.

    Arguments:
      args: The command args to run
      cwd: The dir in which to run the command.
      stdout: The name of the file where we're putting stdout.
      stderr: The name of the file where we're puttin stderr.
      log_dir: The dir to place the stdout and stderr logs, only used if they
        are relative paths. (Defaults to cwd if provided)
      timeout: The timeout for the command in seconds (default: None)
      run_cmd: A command with a signature equal to subprocess.run, that
        will be used to actual evaluate the function in the location.
        (Default: subprocess.run)
    """

    cwd = Path(cwd).resolve()

    log_dir = Path(log_dir if log_dir else cwd).resolve()

    if not Path(stdout).is_absolute():
        stdout = log_dir / stdout
    stdout = Path(stdout).resolve()

    if not Path(stderr).is_absolute():
        stderr = log_dir / stderr
    stderr = Path(stderr).resolve()

    with stdout.open('w') as so, stderr.open('w') as se:
        process = Msys2.run(
            args,
            cwd=cwd,
            stdout=so,
            stderr=se,
            timeout=timeout,
            text=True,
            run_cmd=run_cmd,
        )

        return process

def run_autoreconf(cwd : Union[str,Path],
                   stdout : Union[str,Path] = "autoreconf.stdout",
                   stderr : Union[str,Path] = "autoreconf.stderr",
                   **kwargs,
):
    """
    Runs autoreconf within cwd and places output dumps of stdout and
    stderr in the appropriate locations.

    Arguments:
      cwd: The dir in which to run the command.
      stdout: The name of the file where we're putting stdout.
      stderr: The name of the file where we're puttin stderr.
      **kwargs: see wrap_build_op for all args
    """

    return wrap_build_op(
        ["autoreconf","-if"],
        cwd=cwd,
        stdout=stdout,
        stderr=stderr,
        **kwargs,
    )

def run_configure(cwd : Union[str,Path],
                  stdout : Union[str,Path] = "configure.stdout",
                  stderr : Union[str,Path] = "configure.stderr",
                  **kwargs,
):
    """
    Runs configure within cwd and places output dumps of stdout and
    stderr in the appropriate locations.

    Arguments:
      cwd: The dir in which to run the command.
      stdout: The name of the file where we're putting stdout.
      stderr: The name of the file where we're puttin stderr.
      **kwargs: see wrap_build_op for all args
    """

    cwd = Path(cwd)

    configure = (cwd / "configure").resolve()

    if not configure.exists():
        raise RuntimeError(
            f"Could not find `configure` executable in `{str(cwd)}` "
            "have you made sure you've run `autoreconf -if` in that directory?"
        )

    return wrap_build_op(
        [configure],
        cwd=cwd,
        stdout=stdout,
        stderr=stderr,
        **kwargs,
    )

def run_make(cwd : Union[str,Path],
             stdout : Union[str,Path] = "make.stdout",
             stderr : Union[str,Path] = "make.stderr",
             **kwargs,
):
    """
    Runs make within cwd and places output dumps of stdout and
    stderr in the appropriate locations.

    Arguments:
      cwd: The dir in which to run the command.
      stdout: The name of the file where we're putting stdout.
      stderr: The name of the file where we're puttin stderr.
      **kwargs: see wrap_build_op for all args
    """

    cwd = Path(cwd)

    makefile = (cwd / "Makefile").resolve()

    if not makefile.exists():
        raise RuntimeError(
            f"Could not find Makefile in `{str(cwd)}` "
            "have you made sure you've run `./configure` in that directory?"
        )

    return wrap_build_op(
        ["make"],
        cwd=cwd,
        stdout=stdout,
        stderr=stderr,
        **kwargs,
    )

def get_libs(exe : Union[str,Path],
             cwd : Union[str,Path],
             stdout : Union[str,Path] = "get_libs.stdout",
             stderr : Union[str,Path] = "get_libs.stderr",
             **kwargs,
):
    """
    Places the libraries for an executable in the same directory as the executable
    and places stdout and stderr in the appropriate locations.

    Arguments:
      exe: The executable file
      cwd: The dir in which to run the command.
      stdout: The name of the file where we're putting stdout.
      stderr: The name of the file where we're puttin stderr.
      **kwargs: see wrap_build_op for all args
    """

    cwd = Path(cwd).resolve()

    exe = Path(exe)

    if not Path(exe).is_absolute():
        exe = (cwd / exe).resolve()

    if not exe.exists():
        raise RuntimeError(
            f"Could not find executable `{str(exe)}` "
            "have you made sure you've run `make` where needed?"
        )

    with resources.path('simple_uam.data.fdm','get_libs.py') as get_libs, \
         Msys2.tempdir() as temp_dir: # Need this to ensure path is comprehensible to msys

        get_libs = Path(get_libs).resolve()

        msys2_python = Msys2.bin_root() / 'python3.exe'
        tmp_libs = Path(temp_dir) / 'get_libs.py'

        shutil.copy2(get_libs, tmp_libs)

        return wrap_build_op(
            [msys2_python,tmp_libs,exe,"--copy","--log-level","DEBUG"],
            cwd=cwd,
            stdout=stdout,
            stderr=stderr,
            **kwargs,
        )

def base_build_key():
    """
    Generates the base, unmodified, build key given the reference workspace
    and configuration options.
    """

    ref_workspace = Config[FDMCompileConfig].reference_path

    file_globs = Config[FDMCompileConfig].user_files

    base_key = TDir.read_dir(ref_workspace, file_globs)

    log.info(
        "Generating base key for build process.",
        ref_workspace=str(ref_workspace),
        file_globs=file_globs,
        key_files=[str(f) for f in base_key.files],
    )

    return base_key

def gen_build_key(provided : Optional[TDir]):
    """
    Will generate the normalized build key given the user provided files.
    """

    base_key = base_build_key()

    if not provided:
        return base_key

    if not provided.is_subsumed_by(base_key):
        raise RuntimeError(
            "Build process was provided inputs not in the allowed set. "
        )

    return base_key.overlay(provided)
