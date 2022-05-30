# Why does this file exist, and why not put this in `__main__`?
#
# You might be tempted to import things from `__main__` later,
# but that will cause problems: the code will get executed twice:
#
# - When you run `python -m simple_uam` python will execute
#   `__main__.py` as a script. That means there won't be any
#   `simple_uam.__main__` in `sys.modules`.
# - When you import `__main__` it will get executed again (as a module) because
#   there's no `simple_uam.__main__` in `sys.modules`.

"""Module that contains the command line application."""

import argparse
import sys
from typing import List, Optional

# Importing all the different config dataclasses to ensure that they're loaded
from util.config import Config, PathConfig #noqa
from setup.config import WorkerSetupConfig #noqa
from uam_workspace.config import UAMWorkspaceConfig #noqa
from uam_worker.config import UAMWorkerConfig #noqa

import util.config.tasks
from util.invoke import task, Collection, InvokeProg
from util.logging import get_logger

log = get_logger(__name__)

def main(args: Optional[List[str]] = None) -> int:
    """
    Run the main program.

    This function is executed when you type `simple-uam` or `python -m simple_uam`.

    Arguments:
        args: Arguments passed from the command line.

    Returns:
        An exit code.
    """

    # Setup the invoke program runner class
    program = InvokeProg(
        namespace=Collection.from_module(util.config.tasks),
        version="0.1.0",
    )

    return program.run(argv=args)
