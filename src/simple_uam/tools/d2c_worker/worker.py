
"""
Various setup and development tasks for SimpleUAM Utility Modules.
"""

import shutil
from simple_uam.util.invoke import task, call
from simple_uam.util.config import Config, PathConfig, D2CWorkerConfig
from simple_uam.util.logging import get_logger

from simple_uam.worker.run_worker import run_worker_node
from simple_uam import direct2cad
from dramatiq import get_broker

from pathlib import Path
import json

import subprocess

log = get_logger(__name__)

@task(incrementable=['verbose'])
def run(ctx,
        processes=0,
        threads=0,
        verbose=0):
    """
    Runs the worker node compute process. This will pull tasks from the broker
    and perform them.

    Arguments:
      processes: Number of simultaneous worker processes.
      threads: Number of threads per worker process.
      verbose: Verbosity of output.
    """

    if processes <= 0:
        processes = Config[D2CWorkerConfig].max_processes

    if threads <= 0:
        threads = Config[D2CWorkerConfig].max_threads

    return run_worker_node(
        modules=[__name__],
        processes=processes,
        threads=threads,
        shutdown_timeout=Config[D2CWorkerConfig].shutdown_timeout,
        skip_logging=Config[D2CWorkerConfig].skip_logging,
    )
