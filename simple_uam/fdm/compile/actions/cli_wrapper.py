"""
Various file IO operations useful for local or remote clients.
"""

from simple_uam.workspace.session import Session, session_op
from simple_uam.util.logging import get_logger
from simple_uam.worker import actor, message_metadata
from simple_uam.util.logging import get_logger
from simple_uam.util.config import Config, FDMCompileConfig
from simple_uam.util.system import backup_file, configure_file
from simple_uam.util.system.glob import apply_glob_mapping
from simple_uam.util.system.file_cache import FileCache
from simple_uam.util.system.text_dir import TDir
from contextlib import contextmanager
from simple_uam.fdm.compile.build_ops import gen_build_key
from simple_uam.fdm.compile.workspace import FDMCompileWorkspace
from simple_uam.fdm.compile.session import FDMCompileSession
import json

from pathlib import Path, WindowsPath
from typing import Union, List, Optional, Dict, Callable, TypeVar, Generic
from attrs import define, field

log = get_logger(__name__)

def load_srcs(autopilot_f : Union[None, str, Path] = None,
              autopilot_c : Union[None, str, Path] = None,
              source_root : Union[None, str, Path] = None,
              source_files : Optional[List[Union[str,Path]]] = None,):
    """
    This loads the source files into a TDir object based on the options given.

    Arguments:
      autopilot_f: file to include as `external_autopilot/src/externalAutopilot.f`
        when running this build. (Supersedes any other method of specifying this file)
      autopilot_c: file to include as `external_autopilot/src/external_autopilot.c`
        when running this build. (Supercedes any other methos of specifying this file)
      source_root: The root of the source directory if supplying files with the
        `source_files` argument. This must match the structure of the fdm source
        repo in order to work. (Default: cwd)
      source_files: A list of one or more files, in subdirs of src_root, to be
        overwritten as part of the compile operation. The source files' locations
        must match their locations in the SWRi flight-dynamics-model repo.
        These can be glob patterns.
    """

    if not source_root:
        source_root = Path.cwd()
    source_root = Path(source_root).resolve()

    if not source_files:
        source_files = list()

    def mk_relative(f):
        fp = Path(f)
        if fp.is_absolute() and fp.is_relative_to(source_root):
            return str(fp.relative_to(source_root))
        elif not fp.is_absolute():
            return str(fp)
        else:
            raise RuntimeError(
                f"Path `{str(fp)}` must be a subdir of source directory "
                f"`{str(source_root)}`."
            )

    source_files = [mk_relative(f) for f in source_files]

    source_dir = TDir.read_dir(
        loc=source_root,
        files=source_files,
    )

    if autopilot_f:
        autopilot_f = Path(autopilot_f).resolve()
        source_dir.add_file(
            filepath=autopilot_f,
            dirloc='external_autopilot/src/externalAutopilot.f',
            mkdir=True,
            overwrite=True,
        )

    if autopilot_c:
        autopilot_c = Path(autopilot_c).resolve()
        source_dir.add_file(
            filepath=autopilot_c,
            dirloc='external_autopilot/src/external_autopilot.c',
            mkdir=True,
            overwrite=True,
        )


    return source_dir


def load_metadata(metadata : Union[None, str, Path],
                  cwd : Union[None,str,Path] = None):
    """
    Loads the metadata from file.

    Arguments:
      metadata: The filename of the metadata.json file
      cwd: the working dir for relative paths (Default: cwd)
    """

    if not cwd:
        cwd = Path.cwd()
    cwd = Path(cwd).resolve()

    if not metadata:
        return None

    metadata = Path(metadata)
    if not metadata.is_absolute():
        metadata = cwd / metadata
    metadata = metadata.resolve()

    with metadata.open('r') as fp:
        return json.load(fp)


def cli_format_args(
        metadata : Union[None, str, Path] = None,
        force_autoreconf : bool = False,
        force_configure : bool = False,
        force_make : bool = False,
        autopilot_f : Union[None, str, Path] = None,
        autopilot_c : Union[None, str, Path] = None,
        source_root : Union[None, str, Path] = None,
        source_files : Optional[List[Union[str,Path]]] = None,
        **kwargs,
):
    """
    Formats the command line arguments into ones suitable for an FDM compile
    operation.

    Arguments:
      metadata: name of a json file to include as `user_metadata` in the output
        `metadata.json`.
      force_autoreconf: Force the autoreconf step in the build process
        (implies force_configure)
      force_configure: force configure step in build process
      force_make: force rebuild of the object even if it's in cache.
      autopilot_f: file to include as `external_autopilot/src/externalAutopilot.f`
        when running this build. (Supersedes any other method of specifying this file)
      autopilot_c: file to include as `external_autopilot/src/external_autopilot.c`
        when running this build. (Supercedes any other methos of specifying this file)
      source_root: The root of the source directory if supplying files with the
        `source_files` argument. This must match the structure of the fdm source
        repo in order to work. (Default: cwd)
      source_files: A list of one or more files, in subdirs of src_root, to be
        overwritten as part of the compile operation. The source files' locations
        must match their locations in the SWRi flight-dynamics-model repo.
        These can be glob patterns.
      **kwargs: Additional keyword arguments that will be passed to compile_op.
    """

    metadata = load_metadata(metadata)

    source_dir = load_srcs(
        autopilot_f=autopilot_f,
        autopilot_c=autopilot_c,
        source_root=source_root,
        source_files=source_files,
    )

    source_rep = None if source_dir.empty else source_dir.to_rep()

    op_args = dict(
        srcs=source_rep,
        metadata=metadata,
        force_autoreconf=force_autoreconf,
        force_configure=force_configure,
        force_make=force_make,
        **kwargs,
    )

    return op_args

def cli_compile_wrapper(
        compile_op : Callable,
        metadata : Union[None, str, Path] = None,
        force_autoreconf : bool = False,
        force_configure : bool = False,
        force_make : bool = False,
        autopilot_f : Union[None, str, Path] = None,
        autopilot_c : Union[None, str, Path] = None,
        source_root : Union[None, str, Path] = None,
        source_files : Optional[List[Union[str,Path]]] = None,
        **kwargs,
):
    """
    This wraps an fdm_compile operation with flags and parsers so that it
    is easier to use from a command line. This assumes all arguments, other
    than the first are either paths to files, folders, boolean flags, or short
    strings.

    Arguments:
      compile_op: The operation to wrap usually either `actors.fdm_compile`
        for local evaluation or `actions.fdm_compile.send` for remote operation.
      metadata: name of a json file to include as `user_metadata` in the output
        `metadata.json`.
      force_autoreconf: Force the autoreconf step in the build process
        (implies force_configure)
      force_configure: force configure step in build process
      force_make: force rebuild of the object even if it's in cache.
      autopilot_f: file to include as `external_autopilot/src/externalAutopilot.f`
        when running this build. (Supersedes any other method of specifying this file)
      autopilot_c: file to include as `external_autopilot/src/external_autopilot.c`
        when running this build. (Supercedes any other methos of specifying this file)
      source_root: The root of the source directory if supplying files with the
        `source_files` argument. This must match the structure of the fdm source
        repo in order to work. (Default: cwd)
      source_files: A list of one or more files, in subdirs of src_root, to be
        overwritten as part of the compile operation. The source files' locations
        must match their locations in the SWRi flight-dynamics-model repo.
        These can be glob patterns.
      **kwargs: Additional keyword arguments that will be passed to compile_op.
    """

    log.info(
        "Running cli wrapper for fdm_compile.",
        metadata=metadata,
        force_autoreconf=force_autoreconf,
        force_configure=force_configure,
        force_make=force_make,
        autopilot_f=autopilot_f,
        autopilot_c=autopilot_c,
        source_root=source_root,
        source_files=source_files,
        **{k: str(v) for k,v in kwargs.items()},
    )

    op_args = cli_format_args(
        metadata=metadata,
        force_autoreconf=force_autoreconf,
        force_configure=force_configure,
        force_make=force_make,
        autopilot_f=autopilot_f,
        autopilot_c=autopilot_c,
        source_root=source_root,
        source_files=source_files,
        **kwargs,
    )

    log.info(
        "Wrapping fdm compile op with cli readers.",
        op_module = compile_op.__module__,
        op_name = compile_op.__name__,
        **{str(k): str(v) for k, v in op_args.items()},
    )

    return compile_op(**op_args)
