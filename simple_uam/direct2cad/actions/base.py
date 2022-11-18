
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
from simple_uam.direct2cad.workspace import D2CWorkspace
from simple_uam.fdm.compile.actions.base import with_fdm_compile


from pathlib import Path, WindowsPath
from typing import Union, List, Optional, Dict, Callable, TypeVar, Generic
from attrs import define, field

log = get_logger(__name__)

def start_creo(workspace=None):
    """
    Start creo within the specified workspace, whichever's available if
    none.

    Arguments:
      workspace: The workspace to run this operation in.
      output: File to write output session metadata to, prints to stdout if
        not specified.
    """

    with D2CWorkspace(name="start-creo",number=workspace) as session:
        session.start_creo()

    return session.metadata


def gen_info_files(design : object,
                   metadata : Optional[object] = None,
                   **kwargs):
    """
    gen_info_files as an actor that will perform the task on a worker node
    and return metadata information.

    Arguments:
      design: The design to generate the info files for as a JSON serializable
        python object.
      metadata: An arbitrary JSON serializable object that will be included
        in 'metadata.json' under the 'user_metadata' field.
      **kwargs: Additional args to be passed to the FDM eval workspace.
    """

    with D2CWorkspace(name="gen-info-files",user_metadata=metadata) as session:
        session.write_design(design)
        session.gen_info_files(design)

    return session.metadata


def process_design(design : object,
                   study_params : Optional[List[Dict]] = None,
                   metadata : Optional[object] = None,
                   compile_args : Optional[Dict] = None,
                   **kwargs):
    """
    Processes a design on a worker node and saves the result into a result
    archive on the worker. Returns metadata on the worker used and archive
    created.

    Arguments:
      design: The design to be processed as a JSON serializable object.
      study_params: A list of dictionaries each containing one set of study
        parameters to run analyses for. The list must have at least one entry
        and the dictionaries must all have the same keys set.
      metadata: A JSON serializable metadata object that will be placed
        in 'metadata.json' under the field 'user_metadata'.
      compile_args : Options to be passed to the fdm compile workspace.
      **kwargs: Additional args to be passed to the FDM eval workspace.
    """

    if not compile_args:
        compile_args = dict(
            srcs=None,
            metadata=metadata,
            force_autoreconf=False,
            force_configure=False,
            force_make=False,
        )

    with with_fdm_compile(
            **compile_args,
    ) as cache_result, \
    D2CWorkspace(
        name="process-design",
        user_metadata=metadata,
        **kwargs,
    ) as session:

        if cache_result != None:
            session.extract_fdm_exe(cache_result[0])

        session.process_design(design, study_params=study_params)

    return session.metadata
