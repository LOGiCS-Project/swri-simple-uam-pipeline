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

import argparse
from omegaconf import OmegaConf
from typing import List, Optional
from util.config.manager import Config
from util.config.path_config import PathConfig


def get_parser() -> argparse.ArgumentParser:
    """
    Return the CLI argument parser.

    Returns:
        An argparse parser.
    """
    return argparse.ArgumentParser(prog="simpleuam-utils")


def main(args: Optional[List[str]] = None) -> int:
    """
    Run the main program.

    This function is executed when you type `simpleuam-utils` or `python -m util`.

    Arguments:
        args: Arguments passed from the command line.

    Returns:
        An exit code.
    """

    # parser = get_parser()
    opts = Config.get(PathConfig)
    print(OmegaConf.to_yaml(opts))  # noqa: WPS421 (side-effect in main is fine)
    return 0
