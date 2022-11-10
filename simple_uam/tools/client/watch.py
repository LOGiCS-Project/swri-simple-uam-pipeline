# Why does this file exist, and why not put this in `__main__`?
#
# You might be tempted to import things from `__main__` later,
# but that will cause problems: the code will get executed twice:
#
# - When you run `python -m util` python will execute
#   `__main__.py` as a script. That means there won't be any
#   `util.__main__` in `sys.modules`.
# - When you import `__main__` it will get executed again (as a module) because
#   there's no `util.__main__` in `sys.modules`.

"""Module that contains the command line application."""

from typing import List, Optional
from simple_uam.util.invoke import Collection, InvokeProg, task
from simple_uam.client.watch import poll_results_backend, poll_result_archive
from simple_uam.client.inputs import load_message_info, read_message_info
from simple_uam.util.logging import get_logger
import json

log = get_logger(__name__)

@task
def poll_backend( ctx,
                  msg_info = None,
                  interval = 10,
                  timeout = 600):
    """
    Task to poll the results backend for a particular message and
    print its metadata to stdout when found.

    Arguments:
      msg_info: File to read message info from, if not given assumes it's
        being read from STDIN.
      interval: The polling interval, in seconds. (Default: 10s)
      timeout: The time to wait for a result to appear before giving up.
          Negative numbers implies no timeout. (Default: 600s)
    """

    if msg_info == None:
        msg_info = read_message_info()
    else:
        msg_info = load_message_info(msg_info)

    timeout = None if timeout <= 0 else timeout

    metadata = poll_results_backend(
        msg_info=msg_info,
        interval=interval,
        timeout=timeout,
    )

    print(json.dumps(
        metadata,
        sort_keys=True,
        indent=2,
    ))

@task
def poll_dir( ctx,
              watch_dir = None,
              msg_info = None,
              interval = 10,
              timeout = 600):
    """
    Task to poll the results backend for a particular message and
    print its metadata to stdout when found.

    Arguments:
      watch_dir: location where results archives will appear.
      msg_info: File to read message info from, if not given assumes it's
        being read from STDIN.
      interval: The polling interval, in seconds. (Default: 10s)
      timeout: The time to wait for a result to appear before giving up.
          Negative numbers implies no timeout. (Default: 600s)
    """

    if msg_info == None:
        msg_info = read_message_info()
    else:
        msg_info = load_message_info(msg_info)

    timeout = None if timeout <= 0 else timeout

    metadata = poll_result_archive(
        msg_info=msg_info,
        archive_dir=watch_dir,
        interval=interval,
        timeout=timeout,
    )

    print(json.dumps(
        metadata,
        sort_keys=True,
        indent=2,
    ))
