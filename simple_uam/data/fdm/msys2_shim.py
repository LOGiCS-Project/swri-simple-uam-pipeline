#!/usr/bin/env python3

import subprocess
import argparse
import textwrap
import logging
import shutil
import time
from typing import Optional, Union, Dict, List
from pathlib import Path
from dataclasses import dataclass, field, asdict
import re
import json

log = logging.getLogger(__name__)

def parse_arguments() -> argparse.Namespace:
    """
    Builds that parser and parses the arguments for this script.

    Returns:
      The arguments this script was called with as parsed.
    """

    parser = argparse.ArgumentParser(
        description=textwrap.dedent(
            """
            This is a shim that makes it easier to run commands within an msys2
            session from outside that session.
            """
        )
    )

    parser.add_argument(
        "cmd-file",
        type=str,
        help="File specifying the command the shim is to run.",
        metavar="CMD_FILE",
    )

    levels = ('NONE', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
    parser.add_argument(
        '--log-level',
        default='INFO',
        choices=levels,
        help="The level of logs to show.",
    )

    parser.add_argument(
        "-w",
        "--wait",
        action="store_true",
        help="Hold the terminal window open after the process is finished so output can be seen.",
    )

    return parser.parse_args()

def init_logger(args : argparse.Namespace):
    """
    Start the logger based on available CLI arguments.
    """

    if args.log_level != "NONE":
        log.setLevel(args.log_level)
        log.addHandler(logging.StreamHandler())

def to_cygpath(win_path : str):
    """
    Call the `cygpath` command to convert a windows path into the cygwin
    namespace.
    """

    log.debug(f"Converting path {repr(win_path)} to cygwin form.")

    process = subprocess.run(
        ["cygpath","-m",win_path],
        capture_output=True,
        universal_newlines=True,
    )

    cyg_path = process.stdout.strip()

    log.debug(f"Converted path {repr(win_path)} to {repr(cyg_path)}.")

    return cyg_path

@dataclass
class CmdOptions():
    args : List
    cwd  : Union[Path,str]
    stdin  : Union[None,Path,str] = None
    """ File to read stdin from. """

    stdout : Union[None,Path,str] = None
    """ File to write stdout to. """

    stderr : Union[None,Path,str] = None
    """ File to write stderr to. """

    stop_flag : Union[Path,str] = None
    """ File to create w/ return code when process is done. """

    timeout : Optional[int] = None

def read_cmd_opts(cmd_file : str):
    """
    Reads the command options in from file.
    """

    opts = None

    cmd_file = Path(to_cygpath(cmd_file))

    if not cmd_file.is_absolute():
        raise RuntimeError(f"Command file {str(cmd_file)} must be specified w/ an absolute path")
    elif not cmd_file.exists():
        raise RuntimeError(f"Command file {str(cmd_file)} must exist.")

    with cmd_file.open('r') as cmd_opts:
        opts = json.load(cmd_opts)

    log.debug(f"Read {str(cmd_file)} to get:\n\n{opts}\n")

    return CmdOptions(**opts)

def norm_arg(arg: Union[str,Dict[str,str]]):
    """
    Will resolve and normalize a single argument in the list of args.
    """

    if isinstance(arg,dict) and len(arg) == 1 and 'str' in arg:
        return str
    elif isinstance(arg,dict) and len(arg) == 1 and "path" in arg:
        return Path(to_cygpath(arg["path"]))
    else:
        raise RuntimeError(
            f"Item of type {type(arg)} not allowed in arglist. "
            "The only valid options are either strings or single entry "
            "dictionaries with a key of 'path' and string containing a "
            "pathname to resolve in cygwin form."
        )

def norm_file(filename : Union[None,str,Path]):
    """
    Resolves a file argument if needed.
    """

    if filename == None:
        return None
    elif isinstance(filename, Path):
        return filename # assumes you've got to set how you want
    else:
        return Path(to_cygpath(filename)).resolve()

def norm_cmd_opts(cmd_opts : CmdOptions):
    """
    Will resolve and normalize the various command options parameters.
    """

    cmd_opts.args = [norm_arg(arg) for arg in cmd_opts.args]
    cmd_opts.cwd = norm_file(cmd_opts.cwd)
    cmd_opts.stdin = norm_file(cmd_opts.stdin)
    cmd_opts.stdout = norm_file(cmd_opts.stdout)
    cmd_opts.stderr = norm_file(cmd_opts.stderr)
    cmd_opts.stop_flag = norm_file(cmd_opts.stop_flag)

    return cmd_opts

def validate_cmd_opts(cmd : CmdOptions):
    """
    Checks whether the fields of a normed cmd_opts are valid.
    """

    if not cmd.cwd.exists() or not cmd.cwd.is_dir():
        raise RuntimeError(
            f"`{str(cmd.cwd)}` is not a valid working dir because it "
            "either doesn't exist or isn't a dir."
        )

    if cmd.stdin and not (cmd.stdin.exists() and cmd.stdin.is_file()):
        raise RuntimeError(
            f"`{str(cmd.stdin)}` is specified as STDIN but it "
            "either does not exist or isn't a file."
        )

    if cmd.stderr and cmd.stderr.exists():
        raise RuntimeError(
            f"`{str(cmd.stderr)}` is specified as STDERR but it already exists."
        )

    if cmd.stdout and cmd.stdout.exists():
        raise RuntimeError(
            f"`{str(cmd.stdout)}` is specified as STDOUT but it already exists."
        )

    if cmd.stop_flag and cmd.stop_flag.exists():
        raise RuntimeError(
            f"`{str(cmd.stop_flag)}` is specified as the stop flag but it already exists."
        )

    if cmd.timeout and cmd.timeout < 0:
        raise RuntimeError("Only positive values for timeout are valid.")

def run_cmd_opts(cmd : CmdOptions):
    """
    Actually runs the command specified in the cmd_opts, creating the various
    files and flags as needed.
    """

    process = subprocess.run(
        args=cmd.args,
        cwd=cmd.cwd,
        stdin=cmd.stdin.read_bytes() if cmd.stdin else None,
        timeout=cmd.timeout,
    )

    if cmd.stdout:
        cmd.stdout.write_bytes(process.stdout)

    if cmd.stderr:
        cmd.stderr.write_bytes(process.stderr)

    return process


if __name__ == "__main__":

    args = parse_arguments()
    init_logger(args)
    log.debug(f"args: {args}")

    wait = bool(args.wait)

    cmd_opts = read_cmd_opts(args.cmd_file)
    log.debug(f"initial cmd_opts: {cmd_opts}")

    cmd_opts = norm_cmd_opts(cmd_opts)
    log.debug(f"normed cmd_opts: {cmd_opts}")

    # This lets us capture a decent class of errors in the return message
    # not just the ones involving the timeout.
    stop_data = {"error": "unknown"}
    try:

        validate_cmd_opts(cmd_opts)
        process = run_cmd_opts(cmd_opts,wait=wait)
        stop_data = {"completed": process.returncode}

    except subprocess.TimeoutExpired as err:
        stop_data = {
            "error": "timeout",
            "message": repr(err),
        }

    except Exception as err:
        stop_data = {
            "error": type(err).__name__,
            "message": repr(err),
        }

    finally:
        with cmd.stop_flag.open('w') as fp:
            json.dump(stop_data,fp,indent=2)

    while wait:
        time.sleep(1)
