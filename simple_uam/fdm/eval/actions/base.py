
from simple_uam.workspace.session import Session, session_op
from simple_uam.util.logging import get_logger
from simple_uam.worker import actor, message_metadata
from simple_uam.util.logging import get_logger
from simple_uam.util.config import Config, FDMCompileConfig
from simple_uam.util.system import backup_file, configure_file
from simple_uam.util.system.glob import apply_glob_mapping
from simple_uam.util.system.file_cache import FileCache
from simple_uam.util.system.text_dir import TDir
from contextlib import contextmanager, ExitStack
from simple_uam.fdm.compile.workspace import FDMCompileWorkspace
from simple_uam.fdm.compile.session import FDMCompileSession
from simple_uam.fdm.compile.actions.base import with_fdm_compile
from simple_uam.fdm.eval.workspace import FDMEvalWorkspace
from simple_uam.fdm.eval.session import FDMEvalSession

from pathlib import Path, WindowsPath
from typing import Union, List, Optional, Dict, Callable, TypeVar, Generic
from attrs import define, field

log = get_logger(__name__)

def eval_fdms(inputs : Dict[Union[str,int],object],
              metadata : Optional[object] = None,
              compile_args : Optional[Dict] = None,
              **kwargs):
    """
    Run multiple fdm inputs with the given fdm compilation options.

    Arguments:
      inputs: Map from index strings to input data objects.
      metadata: An arbitrary JSON serializable object that will be included
        in 'metadata.json' under the 'user_metadata' field.
      srcs: A TDir or compatible json representable that has the modified
        source files for the build.
      force_autoreconf: Force the autoreconf step in the build process
        (implies force_configure)
      force_configure: force configure step in build process
      force_make: force rebuild of the object even if it's in cache.
      compile_args : Options to be passed to the fdm compile workspace.
      **kwargs: Additional args to be passed to the FDM eval workspace.
    """

    if not compile_args:
        compile_args = dict()

    with with_fdm_compile(
            **compile_args,
    ) as cache_result, \
    FDMEvalWorkspace(
        name="fdm-eval-inputs",
        user_metadata=metadata,
        **kwargs,
    ) as session:

        if cache_result != None:
            session.extract_fdm_exe(cache_result[0])

        session.eval_fdms(inputs)

    return session.metadata

def eval_fdm(input : object,
             *vargs,
             **kwargs,
):
    """
    Runs a single fdm input with the index '0', other arguments are
    same as eval_fdms.
    """

    inputs = {'0': input}

    return eval_fdms(inputs, *vargs, **kwargs)
