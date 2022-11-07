
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
from contextlib import contextmanager
from copy import deepcopy
from . import base


from pathlib import Path, WindowsPath
from typing import Union, List, Optional, Dict, Callable, TypeVar, Generic
from attrs import define, field


def should_retry(retries_so_far, exception):
    """
    Function that defines whether to retry a particular action.
    In this case we always want to retry if we have no free workspace,
    ignoring any limit in count.
    """
    return retries_so_far < 5 or isinstance(exception, NoFreeWorkspaceException)

actor_args = dict(
    retry_when  = should_retry,
    min_backoff =                1 * 1000, # 1sec
    max_backoff =           1 * 60 * 1000, # 1min
    max_age     = 1 * 24 * 60 * 60 * 1000, # 1day
    priority    = ActorPriority.WORKSPACE_BOUNDED, # Lower priority than default
)

info_actor_args = dict(
    priority    = ActorPriority.WORKSPACE_BOUNDED, # Lower priority than default
    **actor_args,
)

@actor(**info_actor_args)
def gen_info_files(design : object,
                   metadata : Optional[object] =None,
):
    """
    gen_info_files as an actor that will perform the task on a worker node
    and return metadata information.

    Arguments:
      design: The design to generate the info files for as a JSON serializable
        python object.
      metadata: An arbitrary JSON serializable object that will be included
        in 'metadata.json' under the 'user_metadata' field.
    """

    return build.gen_info_files(
        design=design,
        metadata=metadata,
    )

process_actor_args = dict(
    priority    = ActorPriority.CREO_BOUNDED, # Lower priority than workspace bounded.
    **actor_args,
)

@actor(**process_actor_args)
def process_design(design : object,
                   metadata : Optional[object] =None,
                   srcs: Optional[object] = None,
                   force_autoreconf : bool = False,
                   force_configure : bool = False,
                   force_make : bool = False,
):
    """
    gen_info_files as an actor that will perform the task on a worker node
    and return metadata information.

    Arguments:
      design: The design to generate the info files for as a JSON serializable
        python object.
      metadata: An arbitrary JSON serializable object that will be included
        in 'metadata.json' under the 'user_metadata' field.
      srcs: A TDir or compatible json representable that has the modified
        source files for the build.
      metadata: An arbitrary JSON serializable object that will be included
        in 'metadata.json' under the 'user_metadata' field.
      force_autoreconf: Force the autoreconf step in the build process
        (implies force_configure)
      force_configure: force configure step in build process
      force_make: force rebuild of the object even if it's in cache.
    """

    return build.gen_info_files(
        design=design,
        metadata=metadata,
        srcs=srcs,
        force_autoreconf=force_autoreconf,
        force_configure=force_configure,
        force_make=force_make,
    )
