import json
import sys
from pathlib import Path
from typing import Union, List, Optional, Dict, Callable, TypeVar, Generic

from simple_uam.direct2cad.actions.cli_wrapper import load_design, \
    load_study_params
from simple_uam.fdm.compile.actions.cli_wrapper import load_srcs, \
    load_metadata
from simple_uam.fdm.eval.actions.cli_wrapper import load_fdm_input, \
    load_fdm_inputs

def load_message_info(file_name : Union[str,Path],
                      cwd : Union[None, str,Path]):
    """
    Loads, from a file, the message information from a client's call into a
    python object.

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

    with file_name.open('r') as fn:
        return json.load(fn)

def read_message_info():
    """
    Reads, from STDIN, the message information from a client's call into a
    python object.
    """

    return json.load(sys.stdin)

__all__: List[str] = [
    'load_design',
    'load_study_params',
    'load_srcs',
    'load_metadata',
    'load_fdm_input',
    'load_fdm_inputs',
    'load_message_info',
    'read_message_info',
]  # noqa: WPS410 (the only __variable__ we use)
