
from simple_uam.util.logging import get_logger
from urllib.parse import urlparse
from pathlib import Path
from attrs import define,field

from .broker import _BROKER
import dramatiq

import textwrap

log = get_logger(__name__)

def run_worker_node(processes : int,
                    threads: int,
                    shutdown_timeout: int = 600000,
                    skip_logging : bool = False,
):
    """
    Runs a worker node with various settings.

    Arguments:
      processes: Number of forked processes
      threads: Number of forked threads per process
      shutdown_timeout: Worker shutdown timeout in milliseconds.
      skip_logging: skip dramatiq's orthogonal logging process.
    """

    cli_args = dict(
        processes=processes,
        threads=threads,
        worker_shutdown_timeout=shutdown_timeout,
        skip_logging=skip_logging,
    )

    log.info(
        "Running dramatic workers through CLI.",
        **cli_args,
    )

    return dramatiq.cli.main(args=cli_args)
