
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
from simple_uam.direct2cad.workspace import D2CWorkspace
from . import base
from .cli_wrapper import *

import json
from pathlib import Path, WindowsPath
from typing import Union, List, Optional, Dict, Callable, TypeVar, Generic
from attrs import define, field

@task
def start_creo(ctx,
               workspace=None):
    """
    Start creo within the specified workspace, whichever's available if
    none. Prints output to stdout.

    Arguments:
      workspace: The workspace to run this operation in.
    """

    with D2CWorkspace(name="start-creo",number=workspace) as session:
        session.start_creo()

    print(json.dumps(
        session.metadata,
        sort_keys=True,
        indent=2,
    ))

@task
def gen_info_files(
        ctx,
        design = None,
        metadata = None,
        workspace = None,
):
    """
    This will run the gen_info_files operation locally, using the provided source
    files and metadata. This only works on an appropriately configure worker
    node, but does not need the server to run. Running this will populate the
    cache.

    This prints output metadata to stdout.

    Arguments:
      design: The name of the design file to gen info files for.
      metadata: name of a json file to include as `user_metadata` in the output
        `metadata.json`.
      workspace: The direct2cad workspace the operation should be run in, if
        not provided chooses the lowest configured workspace.
    """

    result_metadata = cli_info_wrapper(
        base.gen_info_files,
        design=design,
        metadata=metadata,
        number=workspace,
    )

    print(json.dumps(
        result_metadata,
        sort_keys=True,
        indent="  ",
    ))

@task(iterable=['src_file'])
def process_design(
        ctx,
        design = None,
        study_params = None,
        metadata = None,
        autopilot_f = None,
        autopilot_c = None,
        src_root = None,
        src_file = None,
        autoreconf = False,
        configure = False,
        make = False,
        workspace = None,
        skip_parsing = False,
        permissive_parsing = False,
        strict_parsing = False,
):
    """
    This will run the process operation locally, using the provided source
    files and metadata. This only works on an appropriately configure worker
    node, but does not need the server to run. Running this will populate the
    cache.

    This prints output metadata to stdout.

    Arguments:
      design: The name of the design file to gen info files for.
      study_params: The name of a JSON or CSV design parameters file to use when
        running the direct2cad pipeline.
      metadata: name of a json file to include as `user_metadata` in the output
        `metadata.json`.
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
      autoreconf: Force the autoreconf step in the build process
        (implies configure)
      configure: force configure step in build process
      make: force rebuild of the object even if it's in cache.
      workspace: The direct2cad workspace the operation should be run in, if
        not provided chooses the lowest configured workspace.
      skip_parsing: Should we skip parsing fdm output files into
        nicer formats?
      permissive_parsing: Should be use a more permissive parsing mode for
        fdm dumps?
      strict_parsing: Should we error out when fdm dumps contain
        unrecognized output?
    """

    result_metadata = cli_process_design_wrapper(
        base.process_design,
        design=design,
        study_params=study_params,
        metadata=metadata,
        autopilot_f = autopilot_f,
        autopilot_c = autopilot_c,
        source_root = src_root,
        source_files = src_file,
        force_autoreconf=autoreconf,
        force_configure=configure,
        force_make=make,
        number=workspace,
        skip_fdm_parsing=skip_parsing,
        permissive_fdm_parsing=permissive_parsing,
        strict_fdm_parsing=strict_parsing,
    )

    print(json.dumps(
        result_metadata,
        sort_keys=True,
        indent="  ",
    ))
