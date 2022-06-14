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

    broker = get_broker()

    log.info(
        "Setting up dramatiq broker.",
        type=type(broker).__name__,
        actors=broker.get_declared_actors(),
        queues=broker.get_declared_queues(),
        middleware=[type(m).__name__ for m in broker.middleware],
    )
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

    metadata = dict(design_file=str(design))
    if metadata_json:
        log.info(
            "Loading metadata.",
            metadata=str(metadata_json),
        )
        with metadata_json.open('r') as fp:
            metadata.update(json.load(fp))

    log.info(
        "Sending task gen_info_files to message broker.",
        design=str(design),
    )
    msg = direct2cad.gen_info_files.send(design_data, metadata=metadata)

    log.info(
        "Finished sending task gen_info_files to message broker.",
        design=str(design),
        queue_name=msg.queue_name,
        actor_name=msg.actor_name,
        message_id=msg.message_id,
        **msg.options,
    )

    if not Config[D2CWorkerConfig].backend.enabled:
        log.warning(
            "No result backend provided. Please examine the records archives "\
            "for the generated results.")
        return None

    log.info(
        "Waiting for gen_info_files result.",
    )
    result = msg.get_result(block=True)

    log.info(
        "Received gen_info_files result.",
        result=result,
    )

    if output:
        log.info(
            "Writing session metadata to output file.",
            output=str(output),
        )
        with output.open('w') as fp:
            json.dump(result, fp)
    else:
        print(json.dumps(result, indent="  "))

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

    broker = get_broker()

    log.info(
        "Setting up dramatiq broker.",
        type=type(broker).__name__,
        actors=broker.get_declared_actors(),
        queues=broker.get_declared_queues(),
        middleware=[type(m).__name__ for m in broker.middleware],
    )

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

    metadata = dict(design_file=str(design))
    if metadata_json:
        log.info(
            "Loading metadata.",
            metadata=str(metadata_json),
        )
        with metadata_json.open('r') as fp:
            metadata.update(json.load(fp))

    log.info(
        "Sending task process_design to message broker.",
        design=str(design),
    )

    msg = direct2cad.process_design.send(design_data, metadata=metadata)

    log.info(
        "Finished sending task process_design to message broker.",
        design=str(design),
        queue_name=msg.queue_name,
        actor_name=msg.actor_name,
        message_id=msg.message_id,
        **msg.options,
    )

    if not Config[D2CWorkerConfig].backend.enabled:
        log.warning(
            "No result backend provided. Please examine the records archives "\
            "for the generated results.")
        return None

    log.info(
        "Waiting for process_design result.",
    )
    result = msg.get_result(block=True)

    log.info(
        "Received process_design result.",
        result=result,
    )

    if output:
        log.info(
            "Writing session metadata to output file.",
            output=str(output),
        )
        with output.open('w') as fp:
            json.dump(result, fp)
    else:
        print(json.dumps(result, indent="  "))
