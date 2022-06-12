"""
Various setup and development tasks for SimpleUAM Utility Modules.
"""

import shutil
from simple_uam.util.invoke import task, call
from simple_uam.util.config import Config, PathConfig, D2CWorkspaceConfig
from simple_uam.util.logging import get_logger

from simple_uam.worker.run_worker import run_worker_node
from simple_uam import direct2cad

from pathlib import Path
import json

import subprocess

log = get_logger(__name__)
manager = D2CManager()

@task
def run(processes=Config[D2CWorkspaceConfig].max_processes,
        threads=Config[D2CWorkspaceConfig].max_threads):
    """
    Runs the worker node compute process. This will pull tasks from the broker
    and perform them.

    Arguments:
      processes: Number of simultaneous worker processes.
      threads: Number of threads per worker process.
    """

    return run_worker_node(
        processes=processes,
        threads=threads,
        shutdown_timeout=Config[D2CWorkspaceConfig].shutdown_timeout,
        skip_logging=Config[D2CWorkspaceConfig].skip_logging,
    )

@task
def gen_info_files(ctx,
                 input='design_swri.json',
                 metadata=None,
                 output=None):
    """
    Will write the design info files in the specified
    workspace, and create a new result archive with only the newly written data.
    The workspace will be reset on the next run.

    Arguments:
      input: The design file to read in.
      metadata: The json-format metadata file to include with the query.
        Should be a dictionary.
      output: File to write output session metadata to, prints to stdout if
        not specified.
    """

    design = Path(input).resolve()
    metadata_json = Path(metadata) if metadata else None

    if output:
        output = Path(output).resolve()

    log.info(
        "Loading design data.",
        input=str(design),
    )
    design_data = None
    with design.open('r') as fp:
        design_data = json.load(fp)

    metadata = None
    if metadata_json:
        log.info(
            "Loading metadata.",
            metadata=str(metadata_json),
        )
        with metadata_json.open('r') as fp:
            metadata = json.load(fp)

    result = direct2cad.gen_info_files(design_data, metadata=metadata)

    if not D2CWorkerConfig.backend.enabled:
        log.warning(
            "No result backend provided. Please examine the records archives "\
            "for the generated results.")
        return None


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
                   metadata=None,
                   output=None):
    """
    Runs the direct2cad pipeline on the input design files, producing output
    metadata and a records archive with all the generated files.

    Arguments:
      input: The design file to read in.
      metadata: The json-format metadata file to include with the query.
        Should be a dictionary.
      output: File to write output session metadata to, prints to stdout if
        not specified.
    """

    design = Path(input).resolve()
    metadata_json = Path(metadata) if metadata else None

    if output:
        output = Path(output).resolve()

    log.info(
        "Loading design data.",
        input=str(design),
    )
    design_data = None
    with design.open('r') as fp:
        design_data = json.load(fp)

    metadata = None
    if metadata_json:
        log.info(
            "Loading metadata.",
            metadata=str(metadata_json),
        )
        with metadata_json.open('r') as fp:
            metadata = json.load(fp)

    result = direct2cad.process_design(design_data, metadata=metadata)

    if not D2CWorkerConfig.backend.enabled:
        log.warning(
            "No result backend provided. Please examine the records archives "\
            "for the generated results.")
        return None


    if output:
        log.info(
            "Writing session metadata to output file.",
            output=str(output),
        )
        with output.open('w') as fp:
            json.dump(session.metadata, fp)
    else:
        print(json.dumps(session.metadata, indent="  "))
