
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
from simple_uam.fdm.compile.build_ops import gen_build_key
from simple_uam.fdm.compile.workspace import FDMCompileWorkspace
from simple_uam.fdm.compile.session import FDMCompileSession
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

@actor(**actor_args)
def fdm_compile(srcs : object,
                metadata : Optional[object] =None,
                force_autoreconf : bool = False,
                force_configure : bool = False,
                force_make : bool = False,
):
    """
    An actor, to be used with `send` that will perform compile action on
    an appropriate worker node.

    Arguments:
      srcs: A TDir or compatible json representable that has the modified
        source files for the build.
      metadata: An arbitrary JSON serializable object that will be included
        in 'metadata.json' under the 'user_metadata' field.
      force_autoreconf: Force the autoreconf step in the build process
        (implies force_configure)
      force_configure: force configure step in build process
      force_make: force rebuild of the object even if it's in cache.

    Returns:
      The metadata from either the build session or this particular cached
      session.
    """

    return build.fdm_compile(
        srcs=srcs,
        metadata=metadata,
        force_autoreconf=force_autoreconf,
        force_configure=force_configure,
        force_make=force_make,
    )
