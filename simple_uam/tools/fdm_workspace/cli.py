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
from . import compile, eval

import simple_uam.fdm.compile.actions.local as compile_local
import simple_uam.fdm.eval.actions.local as eval_local

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
    compile_setup_ns = Collection()
    compile_setup_ns.add_task(compile.setup.mkdirs, "dirs")
    compile_setup_ns.add_task(compile.setup.flight_dynamics_model, "fdm_repo")
    compile_setup_ns.add_task(compile.setup.setup_reference, "reference_workspace")

    compile_manage_ns = Collection()
    compile_manage_ns.add_task(compile.manage.delete_locks, "delete_locks")
    compile_manage_ns.add_task(compile.manage.prune_results, "prune_results")
    compile_manage_ns.add_task(compile.manage.workspaces_dir, "workspaces_dir")
    compile_manage_ns.add_task(compile.manage.cache_dir, "cache_dir")
    compile_manage_ns.add_task(compile.manage.results_dir, "results_dir")

    compile_ns = Collection()
    compile_ns.add_collection(compile_setup_ns, "setup")
    compile_ns.add_collection(compile_manage_ns, "manage")
    compile_ns.add_task(compile_local.fdm_compile, "run")

    eval_setup_ns = Collection()
    eval_setup_ns.add_task(eval.setup.mkdirs, "dirs")
    eval_setup_ns.add_task(eval.setup.fdm_env, "fdm_environment")
    eval_setup_ns.add_task(eval.setup.setup_reference, "reference_workspace")

    eval_manage_ns = Collection()
    eval_manage_ns.add_task(eval.manage.delete_locks, "delete_locks")
    eval_manage_ns.add_task(eval.manage.prune_results, "prune_results")
    eval_manage_ns.add_task(eval.manage.workspaces_dir, "workspaces_dir")
    eval_manage_ns.add_task(eval.manage.cache_dir, "cache_dir")
    eval_manage_ns.add_task(eval.manage.results_dir, "results_dir")

    eval_ns = Collection()
    eval_ns.add_collection(eval_setup_ns, "setup")
    eval_ns.add_collection(eval_manage_ns, "manage")
    eval_ns.add_task(eval_local.eval_fdms, "run")

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
    namespace.add_collection(compile_ns, 'compile')
    namespace.add_collection(eval_ns, 'eval')
    # namespace.add_collection(manage_ns, 'manage')
    # namespace.add_collection(tasks_ns, 'tasks')

    # Setup the invoke program runner class
    program = InvokeProg(
        namespace=namespace,
        version="0.1.0",
    )

    return program.run(argv=args)
