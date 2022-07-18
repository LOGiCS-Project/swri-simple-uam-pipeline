
"""
Various setup and development tasks for SimpleUAM Utility Modules.
"""

import shutil
from simple_uam.util.invoke import task, call
from simple_uam.util.config import Config, PathConfig, D2CWorkerConfig
from simple_uam.util.logging import get_logger
from simple_uam.util.system.nssm import NssmService

from pathlib import Path
import json

import subprocess

log = get_logger(__name__)

worker_service = NssmService(
    service_name="SimpleUAMWorker",
    display_name="SimpleUAM Worker Service",
    description="The worker service for SimpleUAM which processes design analysis requests.",
    config=Config[D2CWorkerConfig].service,
    exe="pdm",
    cwd=Config[PathConfig].repo_dir,
    args=['run','suam-worker','run']
)

@task
def install(ctx):
    """
    Installs the SimpleUAM Worker service with NSSM.
    """
    worker_service.install()

@task
def uninstall(ctx, confirm=True):
    """
    Uninstalls the SimpleUAM Worker service with NSSM.

    Arguments:
      confirm: Require a GUI confirmation box before uninstalling.
    """
    worker_service.uninstall()

@task
def configure(ctx):
    """
    (Re)configures the SimpleUAM Worker service with current settings.
    """
    worker_service.configure()

@task
def start(ctx):
    """
    Starts the SimpleUAM Worker service.
    """
    worker_service.start()

@task
def stop(ctx):
    """
    Stops the SimpleUAM Worker service.
    """
    worker_service.stop()

@task
def restart(ctx):
    """
    Restarts the SimpleUAM Worker service.
    """
    worker_service.restart()

@task
def status(ctx):
    """
    Prints the status of the SimpleUAM Worker service.
    """
    return worker_service.restart()

@task
def gui_edit(ctx):
    """
    Opens the NSSM GUI service editor.
    """
    return worker_service.gui_edit()
