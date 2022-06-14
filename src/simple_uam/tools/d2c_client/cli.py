# Why does this file exist, and why not put this in `__main__`?
#
# You might be tempted to import things from `__main__` later,
# but that will cause problems: the code will get executed twice:
#
# - When you run `python -m util` python will execute
#   `__main__.py` as a script. That means there won't be any
#   `util.__main__` in `sys.modules`.
# - When you import `__main__` it will get executed again (as a module) because
#   there's no `util.__main__` in `sys.modules`.

"""Module that contains the command line application."""

from typing import List, Optional
from simple_uam.util.invoke import Collection, InvokeProg, task
from simple_uam.util.logging import get_logger
from . import tasks

log = get_logger(__name__)

def main(args: Optional[List[str]] = None) -> int:
    """
    Run the main program.

    This function is executed when you type `simpleuam-utils` or `python -m util`.

    Arguments:
        args: Arguments passed from the command line.

    Returns:
        An exit code.
    """

    namespace = Collection(
        tasks.process_design,
        tasks.gen_info_files,
    )

    # Setup the invoke program runner class
    program = InvokeProg(
        namespace=namespace,
        version="0.1.0",
    )

    return program.run(argv=args)
