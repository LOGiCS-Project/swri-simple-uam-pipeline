"""
Various setup and development tasks for SimpleUAM Utility Modules.
"""

import shutil
from simple_uam.util.invoke import task, call
from simple_uam.util.config import Config, PathConfig, CraidlConfig
from simple_uam.util.logging import get_logger

import subprocess

log = get_logger(__name__)

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

@task(positional=['design'])
def gen_info_files(ctx,
                   design,
                   output = None,
                   copy_design = False,
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
      copy_design: Do we copy the input design to the output directory?
        Treats string as filename, True as 'design_swri.json'. Default: False

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
