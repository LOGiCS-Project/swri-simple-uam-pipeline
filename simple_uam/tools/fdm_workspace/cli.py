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
from . import build

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
    build_setup_ns = Collection()
    build_setup_ns.add_task(build.setup.mkdirs, "dirs")
    build_setup_ns.add_task(build.setup.flight_dynamics_model, "fdm_repo")
    build_setup_ns.add_task(build.setup.setup_reference, "reference_workspace")

    build_ns = Collection()
    build_ns.add_collection(build_setup_ns, "setup")

    # manage_ns = Collection()
    # manage_ns.add_task(manage.delete_locks, "delete_locks")
    # manage_ns.add_task(manage.prune_results, "prune_results")
    # manage_ns.add_task(manage.workspaces_dir, "workspaces_dir")
    # manage_ns.add_task(manage.cache_dir, "cache_dir")
    # manage_ns.add_task(manage.results_dir, "results_dir")

    # tasks_ns = Collection()
    # tasks_ns.add_task(tasks.start_creo, "start_creo")
    # tasks_ns.add_task(tasks.gen_info_files, "gen_info_files")
    # tasks_ns.add_task(tasks.process_design, "process_design")

    namespace = Collection(
    )
    namespace.add_collection(build_ns, 'build')
    # namespace.add_collection(manage_ns, 'manage')
    # namespace.add_collection(tasks_ns, 'tasks')

    # Setup the invoke program runner class
    program = InvokeProg(
        namespace=namespace,
        version="0.1.0",
    )

    return program.run(argv=args)
