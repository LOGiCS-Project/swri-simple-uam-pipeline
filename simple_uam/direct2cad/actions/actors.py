
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
import dramatiq


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

    return base.gen_info_files(
        design=design,
        metadata=metadata,
    )

# TODO: Setup ala https://dramatiq.io/cookbook.html#rate-limiting .
#       This should allow gen_info_files and other operations in the same
#       workspace to run in parallel.
#
#       Use of the stub backend keeps the rate limit local to this box
#       rather than shared over multiple workers.
#
# from dramatiq.rate_limits import ConcurrentRateLimiter
# from dramatiq.rate_limits.backends import StubBackend
#
# local_backend = StubBackend()
# creo_mutex = ConcurrentRateLimiter(
#     local_backend,
#     "creo_mutex",
#     limit=1,
# )

process_actor_args = dict(
    priority    = ActorPriority.CREO_BOUNDED, # Lower priority than workspace bounded.
    **actor_args,
)

@actor(**process_actor_args)
def process_design(design : object,
                   study_params : Optional[List[Dict]] = None,
                   metadata : Optional[object] =None,
                   compile_args : Optional[Dict] = None,
):
    """
    gen_info_files as an actor that will perform the task on a worker node
    and return metadata information.

    Arguments:
      design: The design to generate the info files for as a JSON serializable
        python object.
      study_params: The study parameters to use for this run of the pipeline.
      metadata: An arbitrary JSON serializable object that will be included
        in 'metadata.json' under the 'user_metadata' field.
      compile_args : Options to be passed to the fdm compile workspace.
    """

    if not compile_args:
        compile_args = dict()

    if 'srcs' not in compile_args:
        compile_args['srcs'] = None

    return base.process_design(
        design=design,
        study_params=study_params,
        metadata=metadata,
        compile_args=compile_args,
    )
