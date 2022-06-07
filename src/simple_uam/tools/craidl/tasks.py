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

@task
def download_server(ctx):
    """
    Downloads, and unpacks the gremlin server stub.
    """
    raise NotImplementedError()

@task
def configure_server(ctx,
                     host = None,
                     port = None,
                     corpus = None):
    """
    Will patch the stub server's config files and copy over the corpus if
    needed.

    Arguments:
      host: The host the server will serve on.
      port: The port the server will server on.
      corpus: The '.graphml' file to be loaded whenever the server starts.

    All three arguments will default to values from 'CraidlConfig's
    'stub_server' entry.
    """
    raise NotImplementedError()

@task
def run_server(ctx):
    """
    Runs the stub server with the configured settings.
    """
    raise NotImplementedError()

@task
def gen_static_corpus(ctx,
                      host = None,
                      port = None,
                      output = None):
    """
    Generates a static corpus from a running corpus server.

    Arguments:
      host: The hostname of the server we connect to.
      port: The port we're connecting to the server on.
      output: The output file to write the corpus dump to.

    All three arguments will default to values from 'CraidlConfig' if not
    specified.
    """
    raise NotImplementedError()

@task
def gen_info_files(ctx,
                   design = None,
                   output = None,
                   random = False,
                   static = None,
                   host = None,
                   port = None):
    """
    Generates the info files for a given design.

    Arguments:
      design: '.json' with design information. Default: 'design_swri.json'
      output: The output **directory** in which to place the files.
        Default: cwd

      random: Choose a random example from the configured examples directory.
        Mutually exclusive with design. Default: False
      static: The static '.json' corpus to use when generating the files.
        Mutually exclusive with host and port. Default: As configured
      host: The hostname of the corpus server to use when generating the files.
        Mutually exclusive with static. Default: As configured
      port: The port of the corpus server to use when generating the files.
        Mutually exclusice with static. Default: As configured
    """
    raise NotImplementedError()
