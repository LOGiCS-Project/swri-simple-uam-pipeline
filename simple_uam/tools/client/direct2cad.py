"""
Various setup and development tasks for SimpleUAM Utility Modules.
"""

import json
import time
import shutil
import zipfile
import dramatiq
import subprocess

from typing import Optional, Union
from pathlib import Path

from simple_uam.util.invoke import task, call
from simple_uam.util.config import Config, PathConfig, BrokerConfig
from simple_uam.util.logging import get_logger
from simple_uam import direct2cad
from simple_uam.worker import has_backend

log = get_logger(__name__)

def load_design(design_file : Path) -> object:
    """
    Loads a design from file.

    Arguments:
      design_file: Path to the design file
    """
    with Path(design_file).open('r') as fp:
        return json.load(fp)

def load_metadata(metadata_file : Union[Path,str,None]) -> dict:
    """
    Loads metadata from file.
    This can be any arbitrary dictionary and its contents will appear in the
    result archive's metadata.json.
    Useful for keeping track of where each call comes from in a larger
    optimization process.

    Arguments:
      metadata_file: Path to the metadata file
    """
    if not metadata_file:
        return dict()
    with Path(metadata_file).open('r') as fp:
        meta = json.load(fp)
        if not isinstance(meta, dict):
            raise RuntimeError("Metadata must be JSON serializable dictionary.")
        return meta

def wait_on_result(
        msg: dramatiq.Message,
        interval: int = 10,
        timeout: int = 600) -> object:
    """
    Uses the dramatiq backend mechanism to wait on a result from a worker.

    Arguments:
      msg: The message from the dramatiq send call.
      interval: The time, in seconds, to wait between each check of the backend.
      timeout: The total time, in seconds, to wait for a result before giving up.
    """

    elapsed = 0
    result = None

    # Loop until result found
    while not result:

        # Try to get Result
        try:
            log.info(f"Checking for result @ {elapsed}s")
            result = msg.get_result(block=False)

        # If no result yet
        except dramatiq.results.ResultMissing as err:

            # Check if we're timed out
            if elapsed >= timeout:
                raise RuntimeError(f"No result found by {elapsed}s")

            # Else wait another interval
            elapsed += interval
            time.sleep(interval)

    return result

def get_result_archive_path(
        result: object,
        results_dir: Path) -> Path:
    """
    Get the name of the specific result archive from the backend produced
    result.

    Arguments:
      result: The result object returned by `wait_on_result`
      results_dir: The directory in which all the results will appear.
    """

    raw_path = Path(result['result_archive'])

    return results_dir / raw_path.name

def get_zip_metadata(
        zip_file: Path) -> Optional[object]:
    """
    Returns the contents of the zip's metadata.json, if it has one.

    Arguments:
      zip_file: The part to the zip we're opening.
    """

    # Open Zip file
    with zipfile.ZipFile(zip_file) as zip:

        meta_file = zipfile.Path(zip) / 'metadata.json'

        # Check if `metadata.json` exists
        if not meta_file.exists() and meta_file.is_file():
            log.info(f"Zip '{str(zip_file)}' has no metadata.json")
            return None

        # If yes, decode its contents
        with meta_file.open('r') as meta:
            return json.load(meta)

def match_msg_to_zip(
        msg: dramatiq.Message,
        zip_file: Path) -> bool:
    """
    Checks whether the given message produced the given zip archive.

    Arguments:
      msg: The dramatiq message we're checking against
      zip_file: The path to the zip we're verifying
    """

    msg_id = msg.message_id

    metadata = get_zip_metadata(zip_file)

    return metadata and msg_id == metadata['message_info']['message_id']

def watch_results_dir(
        msg: dramatiq.Message,
        results_dir: Path,
        interval: int = 10,
        timeout: int = 600) -> Path:
    """
    Checks directory every interval to see if any of the zip files match the
    provided message.

    We recommend using

    Arguments:
      msg: The message we sent to the broker
      results_dir: dir to look for results archive in
      interval: delay between each check of the results_dir
      timeout: time to search for archive before giving up
    """

    elapsed = 0
    seen = dict()

    # Wait till we're out of time or have a result
    while elapsed <= timeout:
        log.info(f"Checking for result @ {elapsed}s")
        for zip_file in results_dir.iterdir():

            # Check if file is a valid zip
            valid_zip = zip_file.is_file()
            valid_zip = valid_zip and '.zip' == zip_file.suffix
            valid_zip = valid_zip and zip_file not in seen

            # Skip further checks if not zip
            if not valid_zip:
                continue

            # return file if match found, else mark as seen.
            log.info(f"Checking zip file: {str(zip_file)}")
            if match_msg_to_zip(msg, zip_file):
                return zip_file
            else:
                seen[zip_file] = True # Using seen as set

        # Wait for next interval
        elapsed += interval
        time.sleep(interval)

    raise RuntimeError(f"No result found by {elapsed}s")

def run_d2c_task(task,
                 design_file: Union[Path,str],
                 results_dir: Union[Path,str],
                 metadata_file: Union[Path,str,None],
                 timeout: int = 600,
                 interval: int = 10,
                 backend: bool = False,
                 polling: bool = False):
    """
    Runs a d2c client task.

    Arguments:
      task: the task to run
      design_file: the file to load the design from
      results_dir: the directory in which to look for results
      metadata_file: optional metadata file to include in metadata.json
      timeout: time to keep looking for results before giving up
      interval: interval with which to check for new results from the backend
        or the poll the results dir for new zip files.
      backend: force use of result backend
      polling: force use of polling
    """

    if not design_file:
        raise RuntimeError("Design file argument is mandatory.")
    design_file = Path(design_file)


    if not results_dir:
        raise RuntimeError("Results dir argument is mandatory.")
    results_dir = Path(results_dir)

    # Load the design from file
    log.info(
        "Loading Design",
        design_file=str(design_file)
    )
    design = load_design(design_file)

    # Load the metadata from file
    log.info(
        "Loading Metadata (if provided)",
        metadata_file = metadata_file,
    )
    metadata = load_metadata(metadata_file)

    # Send the design to worker
    log.info("Sending Design to Broker")
    msg = task.send(design, metadata=metadata)

    # Wait for the result to appear
    log.info("Waiting for results")
    use_backend = backend or (has_backend() and not polling)
    result_archive = None
    result=None

    if use_backend:

        # We get completion notifications from the backend so use that
        result = wait_on_result(
            msg,
            timeout=timeout,
            interval=interval,
        )
        result_archive = get_result_archive_path(result, results_dir)

        log.info(
            "Retrieved result from backend",
            result=result,
            result_archive=result_archive,
        )

    else:

        # No backend, so watch for changes in the results dir
        result_archive = watch_results_dir(
            msg,
            results_dir,
            timeout=timeout,
            interval=interval,
        )
        result = get_zip_metadata(result_archive)

        log.info(
            "Result archive found in results dir",
            result=result,
            result_archive=result_archive,
        )

    return result_archive

@task
def gen_info_files(ctx,
                   design='design_swri.json',
                   results=None,
                   metadata=None,
                   timeout=600,
                   interval=10,
                   backend=False,
                   polling=False):
    """
    Will write the design info files in the specified
    workspace, and create a new result archive with only the newly written data.
    The workspace will be reset on the next run.
    Writes the output archive name to stdout on success.

    Arguments:
      design: The design file to read in. (Mandatory)
      results: Where results files are placed. (Mandatory)
      metadata: The json-format metadata file to include with the query.
        Should be a dictionary.
      timeout: time, in seconds, to keep looking for results before giving up.
      interval: interval, in seconds, with which to check for new results from
        the backend or the poll the results dir for new zip files.
      backend: force use of result backend
      polling: force use of polling
    """

    result_archive = run_d2c_task(
        direct2cad.gen_info_files,
        design_file=design,
        results_dir=results,
        metadata_file=metadata,
        interval=interval,
        timeout=timeout,
        backend=backend,
        polling=polling,
    )

    print(result_archive)

@task
def process_design(ctx,
                   design='design_swri.json',
                   results=None,
                   metadata=None,
                   timeout=600,
                   interval=10,
                   backend=False,
                   polling=False):
    """
    Runs the direct2cad pipeline on the input design files, producing output
    metadata and a result archive with all the generated files.
    Writes the output archive name to stdout on success.

    Arguments:
      design: The design file to read in. (Mandatory)
      results: Where results files are placed. (Mandatory)
      metadata: The json-format metadata file to include with the query.
        Should be a dictionary.
      timeout: time, in seconds, to keep looking for results before giving up.
      interval: interval, in seconds, with which to check for new results from
        the backend or the poll the results dir for new zip files.
      backend: force use of result backend
      polling: force use of polling
    """

    result_archive = run_d2c_task(
        direct2cad.process_design,
        design_file=design,
        results_dir=results,
        metadata_file=metadata,
        timeout=timeout,
        interval=interval,
        backend=backend,
        polling=polling,
    )

    print(result_archive)
