# Why does this file exist, and why not put this in `__main__`?
#
# You might be tempted to import things from `__main__` later,
# but that will cause problems: the code will get executed twice:
#
# - When you run `python -m setup` python will execute
#   `__main__.py` as a script. That means there won't be any
#   `setup.__main__` in `sys.modules`.
# - When you import `__main__` it will get executed again (as a module) because
#   there's no `setup.__main__` in `sys.modules`.

"""Module that contains the command line application."""

from typing import List, Optional
from util.invoke import task, Collection, InvokeProg
from ..config import tasks, WorkerSetupConfig
import util.config.tasks
import setup.tasks.shared
import setup.tasks.worker
import setup.windows.choco

def main(args: Optional[List[str]] = None) -> int:
    """
    Run the main program.

    This function is executed when you type `setup` or `python -m setup`.

    Arguments:
        args: Arguments passed from the command line.

    Returns:
        An exit code.
    """

    # Tasks initialized in root of namespace
    namespace = Collection(
        setup.tasks.shared.mac_address,
    )

    # Import tasks from other files/modules
    namespace.add_collection(
        Collection(
            setup.tasks.shared.dep_pkgs,
            setup.tasks.shared.qol_pkgs,
        ),
        'install',
    )

    # Import tasks from other files/modules
    namespace.add_collection(
        Collection.from_module(setup.tasks.worker),
        'worker',
    )

    # Import tasks from other files/modules
    namespace.add_collection(
        Collection.from_module(setup.windows.choco),
        'choco',
    )

    # Import tasks from other files/modules
    namespace.add_collection(
        Collection.from_module(util.config.tasks),
        'config',
    )

    # Setup the invoke program runner class
    program = InvokeProg(
        namespace=namespace,
        version="0.1.0",
    )

    return program.run()
