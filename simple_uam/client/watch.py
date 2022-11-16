import json
import time
import shutil
from zipfile import ZipFile
import zipfile
import dramatiq
import subprocess
import asyncio
import functools
from simple_uam.worker.broker import get_broker
from pathlib import Path
from typing import Union, List, Optional, Dict, Callable, TypeVar, Generic, \
    Coroutine, AsyncGenerator
from .results import *
from simple_uam.util.logging import get_logger

log = get_logger(__name__)

async def apoll_results_backend( msg_info: object,
                                 interval: int = 10):
    """
    Periodically checks the results backend for whether the particular
    message is complete. If so, will return that result.

    Note: This is an async function and can be used in an asynchronous pipeline.

    Arguments:
      msg_info: The message info we're checking completion for.
      interval: The polling interval, in seconds. (Default: 10s)

    Returns: The same data as the 'metadata.json' from a completed result.
    """

    msg_info = norm_msg_info(msg_info)
    msg_id = message_info_to_id(msg_info)
    msg = mk_dramatiq_message(msg_info)

    elapsed = 0
    result = None

    while not result:

        # Try to get Result
        try:

            log.info(
                f"Checking for result.",
                msg_id = msg_id,
                elapsed = elapsed,
                interval = interval,
            )

            result = msg.get_result(block=False)

        # If no result yet
        except dramatiq.results.ResultMissing as err:

            # Else wait another interval
            await asyncio.sleep(interval)
            elapsed += interval

    return result

async def awatch_archive_dir(archive_dir : Union[str,Path],
                             name_glob : str = "*.zip",
                             name_filter : Optional[Callable[[str], bool]] = None,
                             cwd : Union[None,str,Path] = None,
                             interval: int = 10):
    """
    Watches the archive directory for new archive files and produces an
    iterable of results as they're found.

    Note: This is a generator that will keep chugging along as long as something
    is waiting on it.

    Arguments:
      archive_dir: location where results archives will appear.
      name_glob: glob that we use to select archive files in the directory.
        (Default: '*.zip')
      name_filter: filter function over archive names that will reduce the
        number of files we actually have to check. (Default: const True)
      cwd: The working dir relative to which we'll resolve the file name.
      interval: The polling interval, in seconds. (Default: 10s)

    Returns: An async iterator over the result archives from `archive_dir`.
    """

    if not cwd:
        cwd = Path.cwd()
    cwd = Path(cwd).resolve()

    archive_dir = Path(archive_dir)
    if not archive_dir.is_absolute():
        archive_dir = cwd / archive_dir
    archive_dir = archive_dir.resolve()

    seen = set()
    if name_filter == None:
        name_filter = lambda _: True

    elapsed = 0

    while True:

        files = archive_dir.glob(name_glob)

        for f in files:
            if f not in seen and \
               name_filter(str(f)) and \
               is_result_archive(f,archive_dir):

                yield get_result_metadata(f, archive_dir)

            seen.add(f)

        # Wait another interval
        await asyncio.sleep(interval)
        elapsed += interval

async def apoll_result_archive( msg_info: object,
                                archive_dir : Union[str,Path],
                                cwd : Union[None,str,Path] = None,
                                interval: int = 10):
    """
    Poll and wait for a given result to appear in the archive dir.

    Note: This is an asynchronous coroutine meant to be used as such.

    Arguments:
      msg_info: The message info we're checking completion for.
      archive_dir: location where results archives will appear.
      cwd: The working dir relative to which we'll resolve the file name.
      interval: The polling interval, in seconds. (Default: 10s)

    Returns: The same data as the 'metadata.json' from the completed result
      archive.
    """

    msg_info = norm_msg_info(msg_info)
    name_filter=functools.partial(is_message_archive_name, msg_info=msg_info)

    watcher = awatch_archive_dir(
        archive_dir=archive_dir,
        cwd=cwd,
        name_filter=name_filter,
        interval=interval,
    )

    async for metadata in watcher:
        if msg_info['message_id'] == metadata['message_info']['message_id']:
            return metadata


def poll_results_backend( msg_info: object,
                          interval: int = 10,
                          timeout: Optional[int] = None):
    """
    Periodically checks the results backend for whether the particular
    message is complete. If so, will return that result.

    Arguments:
      msg_info: The message info we're checking completion for.
      interval: The polling interval, in seconds. (Default: 10s)
      timeout: The time to wait for a result to appear before giving up.
          None implies no timeout. (Default: None)

    Returns: The same data as the 'metadata.json' from the completed result
      archive.
    """

    msg_info = norm_msg_info(msg_info)

    return asyncio.run(
        asyncio.wait_for(
            apoll_results_backend(
                msg_info,
                interval
            ),
            timeout,
        )
    )

def poll_result_archive( msg_info: object,
                         archive_dir : Union[str,Path],
                         cwd : Union[None,str,Path] = None,
                         interval: int = 10,
                         timeout: Optional[int] = None):
    """
    Poll and wait for a given result to appear in the archive dir.

    Arguments:
      msg_info: The message info we're checking completion for.
      archive_dir: location where results archives will appear.
      cwd: The working dir relative to which we'll resolve the file name.
      interval: The polling interval, in seconds. (Default: 10s)
      timeout: The time to wait for a result to appear before giving up.
          None implies no timeout. (Default: None)

    Returns: The same data as the 'metadata.json' from the completed result
      archive.
    """

    msg_info = norm_msg_info(msg_info)

    return asyncio.run(
        asyncio.wait_for(
            apoll_result_archive(
                msg_info,
                archive_dir,
                cwd,
                interval
            ),
            timeout,
        )
    )
