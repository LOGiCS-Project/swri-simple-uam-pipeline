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
    sri_ns.add_task(examples.install_examples, "install")

    corpus_db_ns = Collection()
    corpus_db_ns.add_task(examples.list_corpus_db_examples, "list")
    corpus_db_ns.add_task(examples.install_corpus_db_examples, "install")

    examples_ns = Collection()
    examples_ns.add_task(examples.list_examples, 'list')
    examples_ns.add_task(examples.add_examples, 'add')
    examples_ns.add_task(examples.clean_examples, 'clean')
    examples_ns.add_task(examples.examples_dir, 'dir')
    examples_ns.add_collection(sri_ns, 'sri')
    examples_ns.add_collection(corpus_db_ns, 'corpus_db')

    server_ns = Collection()
    server_ns.add_task(stub_server.download_server, 'download')
    server_ns.add_task(stub_server.unpack_server, 'unpack')
    server_ns.add_task(stub_server.configure_server, 'configure')
    server_ns.add_task(stub_server.run_server, 'run')

    corpus_ns = Collection()
    corpus_ns.add_task(stub_server.download_corpus , 'download')
    corpus_ns.add_task(stub_server.install_corpus, 'install')
    corpus_ns.add_task(stub_server.corpus_loc, 'loc')

    static_corpus_ns = Collection()
    static_corpus_ns.add_task(tasks.copy_static_corpus, 'copy')
    static_corpus_ns.add_task(tasks.gen_static_corpus, 'generate')

    namespace = Collection(
        tasks.gen_info_files,
    )
    namespace.add_collection(examples_ns, 'examples')
    namespace.add_collection(server_ns, 'stub_server')
    namespace.add_collection(corpus_ns, 'corpus')
    namespace.add_collection(static_corpus_ns, 'static_corpus')

    # Setup the invoke program runner class
    program = InvokeProg(
        namespace=namespace,
        version="0.1.0",
    )

    return program.run(argv=args)
