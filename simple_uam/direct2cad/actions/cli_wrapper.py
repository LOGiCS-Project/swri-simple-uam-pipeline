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
import csv

from pathlib import Path, WindowsPath
from typing import Union, List, Optional, Dict, Callable, TypeVar, Generic
from attrs import define, field

log = get_logger(__name__)

def load_design(design : Union[str, Path],
                cwd : Union[None,str,Path] = None):
    """
    Loads the design from file.

    Arguments:
      design: The filename of the design_swri.json file
      cwd: the working dir for relative paths (Default: cwd)
    """

    if not cwd:
        cwd = Path.cwd()
    cwd = Path(cwd).resolve()

    design = Path(design)
    if not design.is_absolute():
        design = cwd / design
    design = design.resolve()

    with design.open('r') as fp:
        return json.load(fp)

def load_study_params(study_params : Union[None,str,Path],
                      cwd: Union[None,str,Path] = None):
    """
    Loads the study parameters from file, will use either json or csv format,
    whichever works.

    Arguments:
      study_params: The filename of the json or csv study params file.
      cwd: the working dir for relative paths (Default: cwd)
    """

    if not study_params:
        return None

    if not cwd:
        cwd = Path.cwd()
    cwd = Path(cwd).resolve()

    study_params = Path(study_params)
    if not study_params.is_absolute():
        study_params = cwd / study_params
    study_params = study_params.resolve()

    errs = list()

    try:
        with study_params.open('r') as sp:
            return json.load(sp)
    except Exception as err:
        errs.append(err)

    try:
        with study_params.open('r') as sp:
            reader = csv.DictReader(sp)
            return [row for row in reader]
    except Exception as err:
        errs.append(err)

    raise RuntimeError(
        f"Could not decode study params at `{str(study_params)}` as either "
        "JSON or CSV.", *errs)



def cli_info_args(
        design : Union[str, Path],
        metadata : Union[None, str, Path] = None,
        **kwargs,
):
    """
    Formats the command line arguments into ones suitable for a gen info files
    operation.

    Arguments:
      design: The name of the input design file
      metadata: name of a json file to include as `user_metadata` in the output
        `metadata.json`.
      **kwargs: Additional keyword arguments that will be passed to compile_op.
    """

    metadata_obj = compile_cli.load_metadata(metadata)

    design_obj = load_design(design)

    op_args = dict(
        design=design_obj,
        metadata=metadata_obj,
        **kwargs,
    )

    return op_args

def cli_info_wrapper(
        info_op : Callable,
        design : Union[str, Path],
        metadata : Union[None, str, Path] = None,
        **kwargs,
):
    """
    This wraps an gen_info_files operation with flags and parsers so that it
    is easier to use from a command line. This assumes all arguments, other
    than the first are either paths to files, folders, boolean flags, or short
    strings.

    Arguments:
      info_op: The operation to wrap usually either `actions.gen_info_files`
        for local evaluation or `actors.gen_info_files.send` for remote operation.
      design: name of a design_swri.json to use as input.
      metadata: name of a json file to include as `user_metadata` in the output
        `metadata.json`.
      **kwargs: Additional keyword arguments that will be passed to compile_op.
    """

    log.info(
        "Running cli wrapper for gen_info_files.",
        design=str(design),
        metadata=str(metadata),
        **{str(k): str(v) for k,v in kwargs.items()},
    )

    op_args = cli_info_args(
        design=design,
        metadata=metadata,
        **kwargs,
    )

    log.info(
        "Wrapping gen_info_files op with cli readers.",
        op_module = info_op.__module__,
        op_name = info_op.__name__,
        **{str(k): str(v) for k, v in op_args.items()},
    )

    return info_op(**op_args)

def cli_process_design_args(
        design : Union[str, Path],
        study_params : Union[None, str, Path] = None,
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
    Formats the command line arguments into ones suitable for an FDM compile
    operation.

    Arguments:
      design: name of a design_swri.json to use as input.
      study_params: The name of a JSON or CSV design parameters file to use when
        running the direct2cad pipeline.
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

    metadata_obj = compile_cli.load_metadata(metadata)

    design_obj = load_design(design)

    param_data = load_study_params(study_params)

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

    op_args = dict(
        design=design_obj,
        study_params=param_data,
        metadata=metadata_obj,
        compile_args=compile_args,
        **kwargs,
    )

    return op_args

def cli_process_design_wrapper(
        process_op : Callable,
        design : Union[str, Path],
        study_params : Union[None,str,Path] = None,
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
    This wraps an process_design operation with flags and parsers so that it
    is easier to use from a command line. This assumes all arguments, other
    than the first are either paths to files, folders, boolean flags, or short
    strings.

    Arguments:
      process_op: The operation to wrap usually either `actions.process_design`
        for local evaluation or `actors.process_design.send` for remote operation.
      design: name of a design_swri.json to use as input.
      study_params: The name of a JSON or CSV design parameters file to use when
        running the direct2cad pipeline.
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
        "Running cli wrapper for process_design.",
        design=str(design),
        metadata=str(metadata),
        force_autoreconf=force_autoreconf,
        force_configure=force_configure,
        force_make=force_make,
        autopilot_f=autopilot_f,
        autopilot_c=autopilot_c,
        source_root=source_root,
        source_files=source_files,
        **{k: str(v) for k,v in kwargs.items()},
    )

    op_args = cli_process_design_args(
        design=design,
        study_params=study_params,
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
        "Wrapping fdm process_design op with cli readers.",
        op_module = process_op.__module__,
        op_name = process_op.__name__,
        **{str(k): str(v) for k, v in op_args.items()},
    )

    return process_op(**op_args)
