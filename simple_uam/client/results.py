import json
import time
import shutil
from zipfile import ZipFile
import zipfile
import dramatiq
import subprocess
import asyncio
from simple_uam.worker.broker import get_broker
from pathlib import Path
from typing import Union, List, Optional, Dict, Callable, TypeVar, Generic

def message_info_to_id(msg_info : object):
    """
    Get the message id (GUID) field from the message info object.

    Arguments:
      msg_info: The message_info object that you get from dramatiq.Message.asdict
    """

    if not 'message_id' in msg_info:
        raise RuntimeError(
            "Message Info doesn't have expected 'message_id' field."
        )

    return msg_info['message_id']

def message_id_to_slug(msg_id : str):
    """
    Get the message slug from the message id string.

    Arguments:
      msg_id: The message_id string containing the message's GUID.
    """

    parts = msg_id.split('-')

    if len(parts) != 5:
        raise RuntimeError(
            f"Did not find five segments in message_id `{msg_id}`. "
            "Are you sure this is a valid GUID in the correct format?"
        )

    return parts[-1]

def get_result_metadata(file_name : Union[str,Path],
                        cwd : Union[None, str, Path] = None):
    """
    Get the metadata.json info from the provided result archive.

    Arguments:
      file_name: The name of the result_archive
      cwd: The working directory to use if file_name is relative (Default: cwd)
    """

    if not cwd:
        cwd = Path.cwd()
    cwd = Path(cwd).resolve()

    file_name = Path(file_name)
    if not file_name.is_absolute():
        file_name = cwd / file_name
    file_name = file_name.resolve()

    with ZipFile(file_name, mode='r') as zf, \
         zf.open('metadata.json', mode='r') as mf:

        return json.load(mf)

def is_result_archive(file_name : Union[str,Path],
                      cwd : Union[None, str, Path] = None):
    """
    Is this a zip archive with a valid metadata.json to be a result?

    Arguments:
      file_name: The name of the result_archive
      cwd: The working directory to use if file_name is relative (Default: cwd)
    """

    try:

        metadata = get_result_metadata(file_name, cwd)

        return 'message_info' in metadata and 'session_info' in metadata

    except:

        return False

def is_message_archive_name(file_name : Union[str,Path],
                            msg_info : object):
    """
    Is the name of the file consistent with the provided message info?

    Arguments:
      file_name: The name of the result_archive
      msg_info: The JSON object with the encoded information from the message
    """

    msg_id = message_info_to_id(msg_info)
    msg_slug = message_id_to_slug(msg_id)

    return msg_slug in Path(file_name).name


def is_message_archive(file_name : Union[str, Path],
                       msg_info : object,
                       cwd : Union[None, str, Path] = None):
    """
    Is the file a result for the given message?

    Arguments:
      file_name: The name of the result_archive
      msg_info: The JSON object with the encoded information from the message
      cwd: The working directory to use if file_name is relative (Default: cwd)
    """

    if not is_message_arhive_name(file_name, msg_info):
        return False

    if not is_result_archive(file_name, cwd):
        return False

    metadata = get_result_metadata(file_name, cwd)

    if msg_info['message_id'] != metadata['message_info']['message_id']:
        return False

    return True

def is_redis_message(msg_info : object):
    """
    Is this a message sent with a redis backend?

    Arguments:
      msg_info: The JSON object with the encoded information from the message
    """
    return 'redis_message_id' in msg_info.get('options',dict())

def mk_dramatiq_message(msg_info : object):
    """
    Converts the message info object into a dramatiq.Message that can be
    used when waiting redis or other backends.

    Arguments:
      msg_info: The JSON object with the encoded information from the message
    """

    return dramatiq.Message(
        queue_name = msg_info['queue_name'],
        actor_name = msg_info['actor_name'],
        args = msg_info['args'],
        kwargs = msg_info['kwargs'],
        options = msg_info['options'],
        message_id = msg_info['message_id'],
        message_timestamp = msg_info['message_timestamp'],
    )
