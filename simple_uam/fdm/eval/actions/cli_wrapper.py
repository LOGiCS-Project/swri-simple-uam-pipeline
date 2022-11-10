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
import simple_uam.fdm.compile.actions.cli_wrapper as compile_cli
import json

from pathlib import Path, WindowsPath
from typing import Union, List, Optional, Dict, Callable, TypeVar, Generic
from attrs import define, field
import f90nml

log = get_logger(__name__)

def load_fdm_input(file_name : Union[str,Path],
                   cwd : Union[None,str,Path] = None):
    """
    Reads a single fdm input file into memory. Will try to parse file as
    namelist and json.

    Arguments:
      file_name: The name of or path to the file.
      cwd: The working dir relative to which we'll resolve the file name.
    """

    if not cwd:
        cwd = Path.cwd()
    cwd = Path(cwd).resolve()

    file_name = Path(file_name)
    if not file_name.is_absolute():
        file_name = cwd / file_name
    file_name = file_name.resolve()

    available_types = ['.nml','.json']
    exceptions = list()

    if file_name.suffix in available_types:
        available_types = list(file_name.suffix)

    if '.nml' in available_types:
        try:
            with file_name.open('r') as fn:
                return f90nml.read(fn)
        except Exception as err:
            exceptions.append(err)

    if '.json' in available_types:
        try:
            with file_name.open('r') as fn:
                return json.load(fn)
        except Exception:
            exceptions.append(err)

    raise Exception(exceptions)

def load_fdm_inputs(indices : Optional[List[str]] = None,
                    files : Optional[List[str]] = None,
                    file_map : Optional[Dict[str,str]] = None,
):
    """
    Will take inputs from the command line with optional index names and
    read them into an object suitable for sending to the worker.

    Arguments:
      indices: List of indices for input files.
      files: list of files to map to indices.
      file_map: dictionary of indices to file names.
    """

    inputs = dict()

    if file_map and (indices or files):
        raise RuntimeError(
            "Can only provide file_map or (indices or files) not both."
        )

    if file_map:

        for k,fn in file_map.items():

            inputs[k] = load_fdm_input(fn)

    else:

        for i,fn in enumerate(files):

            k = str(i)

            if i < len(indices):
                k = str(indices[i])

            inputs[k] = load_fdm_input(fn)

    return inputs

def cli_format_args(
        indices : Optional[List[str]] = None,
        files : Optional[List[str]] = None,
        metadata : Union[None, str, Path] = None,
        force_autoreconf : bool = False,
        force_configure : bool = False,
        force_make : bool = False,
        autopilot_f : Union[None, str, Path] = None,
        autopilot_c : Union[None, str, Path] = None,
        source_root : Union[None, str, Path] = None,
        source_files : Optional[List[Union[str,Path]]] = None,
        compile_args : Optional[Dict] = None,
        **kwargs,
):
    """
    Formats the command line arguments into ones suitable for an FDM eval
    operation.

    Arguments:
      indices: A list of names for each input file
      files: A namelist or json input to use in the fdm operation
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

    inputs = load_fdm_inputs(
        indices=indices,
        files=files,
    )

    metadata_obj = compile_cli.load_metadata(metadata)

    if not compile_args:
        compile_args = dict()

    compile_args = compile_cli.cli_format_args(
        metadata=metadata,
        force_autoreconf=force_autoreconf,
        force_configure=force_configure,
        force_make=force_make,
        autopilot_f=autopilot_f,
        autopilot_c=autopilot_c,
        source_root=source_root,
        source_files=source_files,
        **compile_args,
    )

    return dict(
        inputs=inputs,
        metadata=metadata_obj,
        compile_args=compile_args,
        **kwargs,
    )

def cli_eval_wrapper(
        eval_op : Callable,
        indices : Optional[List[str]] = None,
        files : Optional[List[str]] = None,
        metadata : Union[None, str, Path] = None,
        force_autoreconf : bool = False,
        force_configure : bool = False,
        force_make : bool = False,
        autopilot_f : Union[None, str, Path] = None,
        autopilot_c : Union[None, str, Path] = None,
        source_root : Union[None, str, Path] = None,
        source_files : Optional[List[Union[str,Path]]] = None,
        compile_args : Optional[Dict] = None,
        **kwargs,
):
    """
    Formats command line options for the evaluation operation.

    Arguments:
      eval_op: The operation to wrap usually either `actors.eval_fdms`
        for local evaluation or `actions.eval_fdms.send` for remote operation.
      indices: A list of names for each input file
      files: A namelist or json input to use in the fdm operation
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
        "Running cli wrapper for eval_fdms.",
        indices=[str(i) for i in indices],
        files=[str(i) for i in files],
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
        indices=indices,
        files=files,
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
        "Wrapping fdm eval op with cli readers.",
        op_module = eval_op.__module__,
        op_name = eval_op.__name__,
        **{k: str(v) for k, v in op_args.items() if k != 'srcs'},
    )

    return eval_op(**op_args)
