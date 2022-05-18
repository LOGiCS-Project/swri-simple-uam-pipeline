
import argparse
from omegaconf import OmegaConf
from typing import List, Optional
from util.config import Config, PathConfig
from util.invoke import task, Collection, InvokeProg
from util.logging import get_logger

log = get_logger(__name__)

@task
def classes(ctx):
    """
    Prints a list of registered configuration classes
    """
    print(Config.config_names())

@task
def keys(ctx):
    """
    Prints a list of interpolation keys for available config classes
    """
    print(Config.config_keys())

@task
def files(ctx):
    """
    Prints a list of file locations (relative to config_dir) for config classes.
    """
    print(Config.config_files())

@task
def path(ctx, key):
    """
    Prints the list of files examined when loading a particular config
    """
    print(Config.load_path(key))

@task(name='print')
def print_config(ctx, key):
    """
    Prints the currently loaded config data for a given class.
    """
    opts = Config.get(key)
    print(OmegaConf.to_yaml(opts))  # noqa: WPS421 (side-effect in main is fine)
