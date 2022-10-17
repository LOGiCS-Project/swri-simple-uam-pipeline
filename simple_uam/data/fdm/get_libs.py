#!/usr/bin/env python3

import subprocess
import argparse
import textwrap
import logging
import shutil
from typing import Optional, Union, Dict
from pathlib import Path
import re

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
            Will recursively get all the libraries used by a program and
            some combination of print the list and copy the libraries
            into a target directory.
            """
        )
    )

    parser.add_argument(
        "object",
        type=Path,
        help="The path to the object (executable or library) we're gathering dlls for",
        metavar="OBJECT",
    )

    parser.add_argument(
        "target",
        type=Path,
        nargs="?",
        help="The location to place all the dll files. (Default: The dir where the OBJECT is located)",
        default=None,
        metavar="TARGET",
    )

    parser.add_argument(
        "-c",
        "--copy-dlls",
        action="store_true",
        help="Copy the files to the same location as object. Only needed if no target is provided.",
    )

    levels = ('NONE', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
    parser.add_argument(
        '--log-level',
        default='INFO',
        choices=levels,
        help="The level of logs to show.",
    )

    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Don't print the list of dlls to stdout.",
    )

    return parser.parse_args()

def init_logger(args : argparse.Namespace):
    """
    Start the logger based on available CLI arguments.
    """

    if args.log_level != "NONE":
        log.setLevel(args.log_level)
        log.addHandler(logging.StreamHandler())

def norm_paths(args : argparse.Namespace):
    """
    Will normalize and resolve the paths for the object and the target.
    Also checks for correctness.

    Arguments:
      args: The output Namespace from parsing the arguments to the scripts

    Returns:
      obj: The normalized and resolved obj file
      target: The normalized and resolved output target
    """

    obj = Path(args.object).resolve()
    target = None

    if not obj.exists() or not obj.is_file():
        raise RuntimeError(f"The object `{str(obj)}` either does not exist or isn't a file.")

    if args.target:
        target = Path(args.target).resolve()
    elif args.copy_dlls: # handles the copy flag by defaulting the target loc
        target = obj.parent

    if target and (not target.exists() or not target.is_dir()):
        raise RuntimeError(f"The output target `{str(target)}` either does not exists or isn't a directory.")

    return obj, target

def run_ldd(obj : Union[str,Path]):
    """
    Will run ldd on obj and return a dictionary of the various dlls in obj.

    Arguments:
      obj: The object we're inspecting will ldd

    Returns:
      A dict from "library name" to "potential lib file location"
    """

    obj = Path(obj).resolve()

    if not obj.exists() or not obj.is_file():
        raise RuntimeError(f"Cannot run ldd on `{str(obj)}` because it does not exist or isn't a file.")

    log.debug(f"Running ldd on: {str(obj)}")

    ldd_regex = re.compile(r'^\s*([^\s]+)\s+=>\s+((not\sfound)|([^\s]+)\s+(\([x0-9A-z]+\)))$', re.MULTILINE)

    ldd_cmd = ["ldd", obj]

    process = subprocess.run(
        ldd_cmd,
        capture_output=True,
        universal_newlines=True,
    )

    try:
        process.check_returncode()
    except subprocess.CalledProcessError:
        raise RuntimeError(
            f"ldd failed when called on: {str(obj)}\n\n"
            f"stderr:\n\n{process.stderr}\n"
            f"stdout:\n\n{process.stdout}"
        )

    log.debug(f"ldd output:\n\n{process.stdout}")

    deps = dict()
    for match in ldd_regex.findall(process.stdout):
        log.debug(f"found match in output of `{str(obj)}`:\n\n{match}\n")

        lib = match[0]
        loc = None if match[3] == '' else Path(match[3])

        if loc and log.isEnabledFor(logging.DEBUG):
            loc_res = loc.resolve()
            log.debug(f"raw      : {match[3]}")
            log.debug(f"base     : {str(loc)}")
            log.debug(f"resolved : {str(loc_res)}")
            log.debug(f"exists   : {loc_res.exists()}")
            log.debug("")

        deps[lib] = loc.resolve()

    log.debug(f"Final matches for `{str(obj)}` are:\n\n{deps}\n")

    return deps

def get_dlls(obj : Union[str, Path]):
    """
    Gets all the dlls for a particular input object file.

    Arguments:
      obj: The object file we're getting dlls for.

    Returns:
      A dict from dll names to locations.
    """

    obj = Path(obj).resolve()
    visited = set()
    queue = set([obj])
    deps = dict()

    while len(queue) > 0:
        item = queue.pop()
        visited.add(item)
        for name, loc in run_ldd(item).items():
            deps[name] = loc
            if loc and loc not in visited:
                queue.add(loc)

    return deps

def copy_dlls(dlls : Dict[str,Path], target : Union[str,Path]):
    """
    Copies the dlls from wherever they are to the target location.

    Arguments:
      dlls: The map of dll names and locations
      target: The output location to copy to
    """

    target = Path(target).resolve()

    for dll_name, dll_src in dlls.items():
        if dll_src:
            dll_dst = target / dll_src.name

            if dll_dst.exists():
                log.warning(
                    f"WARNING: DLL `{dll_name}` already exists at "
                    f"`{str(dll_dst)}` so skipping copy from "
                    f"`{str(dll_src)}`."
                )
            else:
                log.debug(
                    f"Copying DLL `{dll_name}` from "
                    f"`str(dll_src)` to output at `str(dll_dst)`."
                )
                shutil.copy2(dll_src,dll_dst)

def print_dlls(dlls : Dict[str, Path]):
    """
    Print the list of extant dlls to stdout
    """

    for dll_src in dlls.values():
        if dll_src:
            print(str(dll_src))

if __name__ == "__main__":

    args = parse_arguments()
    init_logger(args)
    log.debug(f"args: {args}")

    obj, target = norm_paths(args)
    log.debug(f"obj: {obj}")
    log.debug(f"target: {target}")

    dlls = get_dlls(obj)
    log.debug(f"Dlls linked recursively to `{str(obj)}`:\n\n{dlls}")

    if not args.quiet:
        print_dlls(dlls)

    if target:
        copy_dlls(dlls, target)
