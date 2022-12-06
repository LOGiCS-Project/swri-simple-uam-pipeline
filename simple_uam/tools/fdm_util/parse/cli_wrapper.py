from contextlib import contextmanager, ExitStack
from pathlib import Path, WindowsPath
from typing import Union, List, Optional, Dict, Callable, TypeVar, Generic
from attrs import define, field
import sys
from simple_uam.util.logging import get_logger

log = get_logger(__name__)

@contextmanager
def format_conversion(
        input_file : Union[str, Path, None] = None,
        output_file : Union[str, Path, None] = None,
        cwd: Union[str, Path, None] = None,
):
    """
    A context manager that wraps a basic file conversion operation.

    It provides a file-like input and output object that your code can read
    from and write to.

    Arguments:
      input_file: If specified it'll read from drive, otherwise STDIN.
      output_file: If provided, this will write to file, otherwise STDOUT.
      cwd: The working directory to operate relative to. (Default: Path.cwd)

    Yields:
      (inp_fd, out_fd): Input and output file descriptors you should use.
    """

    # Normalize cwd
    if not cwd:
        cwd = Path.cwd()
    cwd = Path(cwd).resolve()

    # Normalize input_file
    if input_file:
        input_file = Path(input_file)
        if not input_file.is_absolute():
            input_file = cwd / input_file
        input_file = input_file.resolve()

        if not input_file.exists():
            raise RuntimeError(
                f"Input file `{str(input_file)}` was specified but "
                "that file does not exist."
            )

    # Normalize output_file
    if output_file:
        output_file = Path(output_file)
        if not output_file.is_absolute():
            output_file = cwd / output_file
        output_file = output_file.resolve()

        if output_file.exists():
            raise RuntimeError(
                f"Output file `{str(output_file)}` was specified but "
                "that file already exists."
            )

    # Create the context wrapper
    with ExitStack() as s:

        try:
            in_fd = s.enter_context(input_file.open('r')) \
                if input_file else sys.stdin
            out_fd = s.enter_context(output_file.open('w')) \
                if output_file else sys.stdout

            yield (in_fd, out_fd)
        except Exception as exc:

            # log.exception(
            #     "Exception while converting fdm file.")

            raise exc
