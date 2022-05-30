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
import simple_uam.root_dev.tasks
from util.invoke import Collection, InvokeProg, task
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

    print(sys.argv)
    print(args)

    # Setup the invoke program runner class
    program = InvokeProg(
        namespace=Collection.from_module(simple_uam.root_dev.tasks),
        version="0.1.0",
    )

    return program.run(argv=args)

def docs_serve(args: Optional[List[str]] = None) -> int:

    docs_args = argparse.ArgumentParser(
        description="Compile and serve the documentation on a local server.")

    docs_args.add_argument(
        'host',
        type=str,
        default="0.0.0.0",
        help="The host to serve the docs from.",
    )

    docs_args.add_argument(
        'port',
        type=int,
        default=8000,
        help="The port to serve the docs on.",
    )

    args = docs_args.parse_args()
