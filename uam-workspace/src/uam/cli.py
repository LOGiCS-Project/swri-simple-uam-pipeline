# Why does this file exist, and why not put this in `__main__`?
#
# You might be tempted to import things from `__main__` later,
# but that will cause problems: the code will get executed twice:
#
# - When you run `python -m uam` python will execute
#   `__main__.py` as a script. That means there won't be any
#   `uam.__main__` in `sys.modules`.
# - When you import `__main__` it will get executed again (as a module) because
#   there's no `uam.__main__` in `sys.modules`.

"""Module that contains the command line application."""

import argparse
from typing import List, Optional
from util.invoke import task, Collection, InvokeProg
from .config import tasks, UamWorkspaceConfig

@task
def example_task(ctx, arg):
    """
    An example task with one argument.
    """
    print(f"Example Task: {arg}")

def main(args: Optional[List[str]] = None) -> int:
    """
    Run the main program.

    This function is executed when you type `uam-utils` or `python -m uam`.

    Arguments:
        args: Arguments passed from the command line.

    Returns:
        An exit code.
    """


    # Tasks initialized in this file
    namespace = Collection(
        example_task,
    )

    # Import tasks from other files/modules
    namespace.add_collection(
        Collection.from_module(tasks),
        'config',
    )

    # Setup the invoke program runner class
    program = InvokeProg(
        namespace=namespace,
        version="0.1.0",
    )

    return program.run()
