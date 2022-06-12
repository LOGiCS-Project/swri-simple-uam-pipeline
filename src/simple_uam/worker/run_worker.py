
from simple_uam.util.logging import get_logger
from urllib.parse import urlparse
from pathlib import Path
from typing import List, Optional
from attrs import define,field,asdict

from .broker import _BROKER
from dramatiq import get_broker
from dramatiq.cli import main

import textwrap

log = get_logger(__name__)

@define
class RunArgs():
    """
    Proxy for the ParsedArguments that dramatiq.cli.main expects
    as input.
    """

    processes : int = field()
    threads : int = field()
    worker_shutdown_timeout : int = field()
    skip_logging : bool = field()
    path : List[str] = field(factory=list)
    use_spawn : bool = field(default=False)
    pid_file : Optional[str] = field(default=None)
    forks : List[str] = field(factory=list)
    verbose : int = field(default=0)
    watch : Optional[str] = field(default=None)
    log_file : Optional[str] = field(default=None)
    broker : Optional[str] = field(default="simple_uam.worker.broker")
    modules : List[str] = field(factory=list)
    queues : List[str] = field(factory=list)

def run_worker_node(modules : list,
                    processes : int,
                    threads: int,
                    shutdown_timeout: int = 600000,
                    skip_logging : bool = False,
                    verbose : int = 0
):
    """
    Runs a worker node with various settings.

    Arguments:
      modules: List of modules to load, either the object or their names.
      processes: Number of forked processes
      threads: Number of forked threads per process
      shutdown_timeout: Worker shutdown timeout in milliseconds.
      skip_logging: skip dramatiq's orthogonal logging process.
      verbose: Controls verbosity of dramatiq worker.
    """

    broker = get_broker()

    log.info(
        "Setting up dramatiq broker.",
        type=type(broker).__name__,
        actors=broker.get_declared_actors(),
        queues=broker.get_declared_queues(),
        middleware=[type(m).__name__ for m in broker.middleware],
    )

    cli_args = RunArgs(
        processes=processes,
        threads=threads,
        worker_shutdown_timeout=shutdown_timeout,
        skip_logging=skip_logging,
        verbose=verbose,
        modules=[getattr(m,'__name__',m) for m in modules],
    )

    log.info(
        "Running dramatiq worker with args.",
        **asdict(cli_args),
    )

    return main(args=cli_args)
