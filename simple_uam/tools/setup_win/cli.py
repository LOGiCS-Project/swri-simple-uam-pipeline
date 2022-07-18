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

from . import shared, worker, license_server, broker, choco, graph_server

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

    # Tasks initialized in root of namespace
    namespace = Collection(
        shared.mac_address,
        shared.clear_cache,
        shared.disable_firewall,
    )

    # Collect all choco install tasks
    install = Collection()
    install.add_task(worker.dep_pkgs, name='worker-deps')
    install.add_task(license_server.choco_pkgs, name='license-deps')
    install.add_task(broker.choco_pkgs, name='broker-deps')
    install.add_task(shared.qol_pkgs, name='qol-deps')
    install.add_task(shared.global_pkgs, name='global-deps')
    install.add_task(graph_server.choco_pkgs, name='graph-deps')
    namespace.add_collection(install, name='install')

    # Import tasks from other files/modules
    namespace.add_collection(
        Collection.from_module(worker),
        'worker',
    )

    # Import tasks from other files/modules
    namespace.add_collection(
        Collection.from_module(broker),
        'broker',
    )

    # Import tasks from other files/modules
    namespace.add_collection(
        Collection.from_module(license_server),
        'license_server',
    )

    namespace.add_collection(
        Collection.from_module(graph_server),
        'graph_server',
    )

    # Import tasks from other files/modules
    namespace.add_collection(
        Collection.from_module(choco),
        'choco',
    )

    # Setup the invoke program runner class
    program = InvokeProg(
        namespace=namespace,
        version="0.1.0",
    )

    return program.run(argv=args)
