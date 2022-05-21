from omegaconf import OmegaConf, read_write

from util.config import Config
from util.invoke import task
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
    Prints the list of files examined when loading a particular config to STDOUT.
    """
    print([str(p) for p in Config.load_path(key)])


@task(name="print")
def print_config(ctx, key, resolved=False):
    """
    Prints the currently loaded config data for a given class to STDOUT

    Arguments:
       key: The class name, interpolation key, or config file name of the
            config to print out. Can be given positionally.
       resolve: Should we resolve all the interpolations before printing?
    """
    opts = Config.get(key)
    if resolved:
        with read_write(opts):
            OmegaConf.resolve(opts)
    print(OmegaConf.to_yaml(opts))  # noqa: WPS421 (side-effect in main is fine)


@task(
    positional=["config"],
    iterable=["config"],
)
def write_current(ctx, config=None, mkdir=True, write_all=False, overwrite=False, comment=True):
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

    # log.info("Writing out configs",
    #          config=config,
    #          mkdir=mkdir,
    #          write_all=write_all,
    #          overwrite=overwrite,
    #          comment=comment)

    Config.write_configs(config, mkdir=mkdir, write_all=write_all, overwrite=overwrite, comment=comment)
