"""
Various setup and development tasks for SimpleUAM Utility Modules.
"""

import shutil
from simple_uam.util.invoke import task, call
from simple_uam.util.config import Config, PathConfig, WinSetupConfig
from simple_uam.util.logging import get_logger

from simple_uam.d2c_workspace.manager import D2CManager
from simple_uam.d2c_workspace.session import D2CSession
from simple_uam.d2c_workspace.workspace import D2CWorkspace

import subprocess

log = get_logger(__name__)
manager = D2CManager()

@task
def build_cad(ctx,
              design='design_swri.json',
              output=None,
              workspace=None):

    # load the design
    design = ...

    with D2CWorkspace(number=int(workspace)) as session:
        session.build_cad(design)

    out_data = {**session.metadata}
    out_data['result-archive'] = session.result_archive

    # Write output to file & IO
