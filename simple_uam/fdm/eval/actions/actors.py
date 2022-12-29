
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
from simple_uam.fdm.eval.workspace import FDMEvalWorkspace
from simple_uam.fdm.eval.session import FDMEvalSession
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
def eval_fdms(inputs : Dict[Union[str,int],object],
              metadata : Optional[object] = None,
              compile_args : Optional[Dict] = None,
              skip_fdm_parsing : bool = False,
              permissive_fdm_parsing : bool = False,
              strict_fdm_parsing : bool = False,
):
    """
    An actor, to be used with `send` that will perform the fdm eval action on
    an appropriate worker node.

    Arguments:
      inputs: Map from index strings to input data objects.
      metadata: An arbitrary JSON serializable object that will be included
        in 'metadata.json' under the 'user_metadata' field.
      compile_args : Options to be passed to the fdm compile workspace.
      skip_fdm_parsing: Should we skip parsing fdm output files into
        nicer formats?
      permissive_fdm_parsing: Should be use a more permissive parsing mode for
        fdm dumps?
      strict_fdm_parsing: Should we error out when fdm dumps contain
        unrecognized output?
    """

    fdm_to_json_opts = dict(
        permissive=permissive_fdm_parsing,
        strict=strict_fdm_parsing,
    )

    return base.eval_fdms(
        inputs=inputs,
        metadata=metadata,
        compile_args=compile_args,
        skip_fdm_parsing=skip_fdm_parsing,
        fdm_to_json_opts=fdm_to_json_opts,
    )
