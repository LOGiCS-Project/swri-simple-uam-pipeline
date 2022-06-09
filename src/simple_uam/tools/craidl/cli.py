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
from . import tasks, examples, stub_server

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


    sri_ns = Collection()
    sri_ns.add_task(examples.download_examples, "download")
    sri_ns.add_task(examples.download_examples, "install")

    examples_ns = Collection()
    examples_ns.add_task(examples.list_examples, 'list')
    examples_ns.add_task(examples.add_examples, 'add')
    examples_ns.add_task(examples.clean_examples, 'clean')
    examples_ns.add_collection(sri_ns, 'sri')

    server_ns = Collection()
    server_ns.add_task(stub_server.download_server, 'download')
    server_ns.add_task(stub_server.unpack_server, 'unpack')
    server_ns.add_task(stub_server.configure_server, 'configure')
    server_ns.add_task(stub_server.run_server, 'run')

    namespace = Collection(
        tasks.gen_static_corpus,
        tasks.gen_info_files,
    )

    namespace.add_collection(examples_ns, 'examples')
    namespace.add_collection(server_ns, 'stub_server')
    # Setup the invoke program runner class
    program = InvokeProg(
        namespace=namespace,
        version="0.1.0",
    )

    return program.run(argv=args)
