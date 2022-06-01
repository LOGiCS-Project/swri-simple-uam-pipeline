# Why does this file exist, and why not put this in `__main__`?
#
# You might be tempted to import things from `__main__` later,
# but that will cause problems: the code will get executed twice:
#
# - When you run `python -m uam_workspace` python will execute
#   `__main__.py` as a script. That means there won't be any
#   `uam_workspace.__main__` in `sys.modules`.
# - When you import `__main__` it will get executed again (as a module) because
#   there's no `uam_workspace.__main__` in `sys.modules`.

"""Module that contains the command line application."""

from typing import List, Optional
from util.logging import get_logger

log = get_logger(__name__)

def main(args: Optional[List[str]] = None) -> int:
    """
    Run the main program.

    This function is executed when you type `uam-worker` or `python -m uam_workspace`.

    Arguments:
        args: Arguments passed from the command line.

    Returns:
        An exit code.
    """

    raise NotImplementedError()

    # Setup the invoke program runner class
    program = InvokeProg(
        namespace=Collection.from_module(util.dev.tasks),
        version="0.1.0",
    )

    return program.run(args)