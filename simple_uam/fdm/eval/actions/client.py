
from simple_uam.workspace.session import Session, session_op
from simple_uam.workspace.workspace import NoFreeWorkspaceException
from simple_uam.util.logging import get_logger
from simple_uam.worker import actor, message_metadata, ActorPriority
from simple_uam.util.logging import get_logger
from simple_uam.util.config import Config, FDMCompileConfig
from simple_uam.util.system import backup_file, configure_file
from simple_uam.util.system.glob import apply_glob_mapping
from simple_uam.util.system.file_cache import FileCache
from simple_uam.util.system.text_dir import TDir
from simple_uam.util.invoke import task, call
from contextlib import contextmanager
from . import base, actors
from .cli_wrapper import cli_eval_wrapper

import json
from pathlib import Path, WindowsPath
from typing import Union, List, Optional, Dict, Callable, TypeVar, Generic
from attrs import define, field

@task(iterable=['src_file','input_file'])
def eval_fdm(
        ctx,
        input_file,
        autopilot_f = None,
        autopilot_c = None,
        src_root = None,
        src_file = None,
        metadata = None,
        autoreconf = False,
        configure = False,
        make = False,
):
    """
    Evaluates the FDM tool remotely on one or more inputs.

    This print output metadata to stdout.

    Arguments:
      input_file: A specific FDM input file to process. Can be given multiple
        times in order to process multiple files. Files will processed in the
        order given.
      autopilot_f: file to include as `external_autopilot/src/externalAutopilot.f`
        when running this build. (Supersedes any other method of specifying this file)
      autopilot_c: file to include as `external_autopilot/src/external_autopilot.c`
        when running this build. (Supercedes any other methos of specifying this file)
      src_root: The root of the source directory if supplying files with the
        `source_files` argument. This must match the structure of the fdm source
        repo in order to work. (Default: cwd)
      src_file: A list of one or more files, in subdirs of src_root, to be
        overwritten as part of the compile operation. The source files' locations
        must match their locations in the SWRi flight-dynamics-model repo.
        These can be glob patterns, and provided multiple times.
      metadata: name of a json file to include as `user_metadata` in the output
        `metadata.json`.
      autoreconf: Force the autoreconf step in the build process
        (implies configure)
      configure: force configure step in build process
      make: force rebuild of the object even if it's in cache.
    """

    result_metadata = cli_eval_wrapper(
        actors.eval_fdms.send,
        indices = list(),
        files = input_file,
        autopilot_f = autopilot_f,
        autopilot_c = autopilot_c,
        source_root = src_root,
        source_files = src_file,
        metadata=metadata,
        force_autoreconf=autoreconf,
        force_configure=configure,
        force_make=make,
    )

    print(json.dumps(
        result_metadata.asdict(),
        sort_keys=True,
        indent="  ",
    ))
