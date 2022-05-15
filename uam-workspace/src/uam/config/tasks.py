from util.config import Config
from util.invoke import task, Collection, InvokeProg
from omegaconf import OmegaConf

@task
def list_classes(ctx):
    """
    Prints a list of registered configuration classes
    """
    print(Config.config_names())

@task
def list_keys(ctx):
    """
    Prints a list of interpolation keys for available config classes
    """
    print(Config.config_keys())

@task
def list_files(ctx):
    """
    Prints a list of file locations (relative to config_dir) for config classes.
    """
    print(Config.config_files())

@task
def examine_load_path(ctx, key):
    """
    Prints the list of files examined when loading a particular config

    Arguments:
        key: The class_name, interpolation_key, or file_name of the config you want
             to examine.
    """
    print(Config.load_path(key))

@task
def print_config(ctx, key):
    """
    Prints the currently loaded config data for a given class.

    Arguments:
        key: The class_name, interpolation_key, or file_name of the config you want
             to examine.
    """
    opts = Config.get(key)
    print(OmegaConf.to_yaml(opts))  # noqa: WPS421 (side-effect in main is fine)