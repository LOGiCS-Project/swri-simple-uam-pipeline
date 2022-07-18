"""
Various setup and development tasks for SimpleUAM Utility Modules.
"""

import shutil
from simple_uam.util.invoke import task, call
from simple_uam.util.config import Config, PathConfig, D2CWorkspaceConfig
from simple_uam.util.logging import get_logger

from simple_uam.direct2cad.manager import D2CManager
from simple_uam.direct2cad.session import D2CSession
from simple_uam.direct2cad.workspace import D2CWorkspace

from pathlib import Path
import json

import subprocess

log = get_logger(__name__)
manager = D2CManager()

@task
def start_creo(ctx,
                  workspace=None,
                  output=None):
    """
    Start creo within the specified workspace, whichever's available if
    none.

    Arguments:
      workspace: The workspace to run this operation in.
      output: File to write output session metadata to, prints to stdout if
        not specified.
    """

    if output:
        output = Path(output)

    with D2CWorkspace(name="start-creo",number=workspace) as session:
        session.start_creo()

    if output:
        log.info(
            "Writing session metadata to output file.",
            output=str(output),
        )
        with output.open('w') as fp:
            json.dump(session.metadata, fp)
    else:
        print(json.dumps(session.metadata, indent="  "))

@task
def gen_info_files(ctx,
                 input='design_swri.json',
                 workspace=None,
                 output=None):
    """
    Will write the design info files in the specified
    workspace, and create a new result archive with only the newly written data.
    The workspace will be reset on the next run.

    Arguments:
      input: The design file to read in.
      workspace: The workspace to run this operation in.
      output: File to write output session metadata to, prints to stdout if
        not specified.
    """

    design = Path(input).resolve()

    if output:
        output = Path(output).resolve()

    log.info(
        "Loading design data.",
        input=str(design),
    )
    design_data = None
    with design.open('r') as fp:
        design_data = json.load(fp)

    with D2CWorkspace(name="gen-info-files", number=workspace) as session:
        session.write_design(design_data)
        session.gen_info_files(design_data)

    if output:
        log.info(
            "Writing session metadata to output file.",
            output=str(output),
        )
        with output.open('w') as fp:
            json.dump(session.metadata, fp)
    else:
        print(json.dumps(session.metadata, indent="  "))

@task
def process_design(ctx,
                   input='design_swri.json',
                   workspace=None,
                   output=None):
    """
    Runs the direct2cad pipeline on the input design files, producing output
    metadata and a results archive with all the generated files.

    Arguments:
      design: The design file to read in.
      workspace: The workspace to run this operation in.
      output: File to write output session metadata to, prints to stdout if
        not specified.
    """

    design = Path(input)

    if output:
        output = Path(output)

    log.info(
        "Loading design data.",
        input=str(design),
    )

    design_data = None
    with design.open('r') as fp:
        design_data = json.load(fp)

    with D2CWorkspace(name="process-design",number=workspace) as session:
        session.process_design(design_data)

    if output:
        log.info(
            "Writing session metadata to output file.",
            output=str(output),
        )
        with output.open('w') as fp:
            json.dump(session.metadata, fp)
    else:
        print(json.dumps(session.metadata, indent="  "))
