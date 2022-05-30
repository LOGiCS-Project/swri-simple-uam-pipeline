from omegaconf import OmegaConf, read_write

from util.config import Config
from util.invoke import task
from util.logging import get_logger

log = get_logger(__name__)

@task
def dir(ctx, all=False):
    """
    Prints the current terminal config directory.

    Arguments:
        all: Print all config directories in load order (higher priority last).
    """
    if all:
        for d in Config.config_dirs:
            print(str(d))
    else:
        print(str(Config.config_dirs[-1]))

@task
def file(ctx, key, all=False):
    """
    Prints the terminal file examined when loading a particular config.

    Arguments:
        all: Print all the files examined in load order (highest priority last).
    """
    if all:
        for p in Config.load_path(key):
            print(str(p))
    else:
        print(str(Config.load_path(key)[-1]))

@task
def list_classes(ctx):
    """
    Prints a list of registered configuration classes
    """
    for n in Config.config_names():
        print(n)

@task
def list_keys(ctx):
    """
    Prints a list of interpolation keys for available config classes
    """
    for k in Config.config_keys():
        print(k)

@task
def list_files(ctx):
    """
    Prints a list of file locations (relative to config_dir) for config classes.
    """
    for f in Config.config_files():
        print(f)


@task(name="print")
def print_config(ctx, key, resolved=False):
    """
    Prints the currently loaded config data for a given class to STDOUT

    Arguments:
       key: The class name, interpolation key, or config file name of the
            config to print out. Can be given positionally.
       resolve: Should we resolve all the interpolations before printing?
    """
    opts = Config.get_omegaconf(key)
    if resolved:
        with read_write(opts):
            OmegaConf.resolve(opts)
    print(OmegaConf.to_yaml(opts))  # noqa: WPS421 (side-effect in main is fine)


@task(
    positional=["config"],
    iterable=["config"],
)
def write(ctx, config=None, mkdir=True, write_all=False, overwrite=False, comment=True):
    """
    Writes the current configuration out to file in the appropriate location.

    Arguments:
      config (default=all configs): The identifier for the configuration to be
        printed out. This argument can be provided multiple times to specify
        multiple config files.
      mkdir (default=True): Do we create the config directories if needed.
      write_all (default=False): Do we write the config files for all possible
        modes? Otherwise, only write the file for the current run-mode.
      overwrite (default=False): Do we overwrite existing files (creating
        backups as needed)? Otherwise, skip existing config files.
      comment (default=True): Should the configs be written as a block comment?
        Otherwise, write the raw yaml directly.
    """

    # Normalize arg for call
    if config == []:
        config = None

    Config.write_configs(
        config,
        mkdir=mkdir,
        write_all=write_all,
        overwrite=overwrite,
        comment=comment
    )
