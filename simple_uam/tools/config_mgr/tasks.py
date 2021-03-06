from omegaconf import OmegaConf, read_write

from simple_uam.util.config.manager import Config
from simple_uam.util.invoke import task
from simple_uam.util.logging import get_logger

log = get_logger(__name__)

@task
def dir(ctx, all=False):
    """
    Prints the current terminal config directory.

    Arguments:
        all: Print all config directories in load order (higher priority last).
    """
    if all:
        for d in Config().config_dirs:
            print(str(d))
    else:
        print(str(Config().config_dirs[-1]))

@task
def file(ctx, config=None, all=False):
    """
    Prints the terminal file examined when loading a particular config.

    Arguments:
        config: the file to examine
        all: Print all the files examined in load order (highest priority last).
    """
    if not config:
        raise RuntimeError("No config file identifier provided.")
    elif all:
        for p in Config().load_path(config):
            print(str(p))
    else:
        print(str(Config().load_path(config)[-1]))

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

@task(name="print", iterable=['config'])
def print_config(ctx, config=None, resolved=False, all=False):
    """
    Prints the currently loaded config data for a given class to STDOUT

    Arguments:
       config: The class name, interpolation key, or config file name of the
            config to print out. Can be given multiple times.
       resolve: Should we resolve all the interpolations before printing?
       all: Print all the configs, mutually exclusive with key.
    """

    keys = config

    if len(keys) == 0 and all:
        keys = [str(k) for k in Config().file_map.keys()]
    elif len(keys) == 0:
        raise RuntimeError("Please specify keys to print or '--all'")

    for k in keys:
        config_class = Config()._get_config_class(k)
        config_data = Config().config_types[config_class]
        filename = str(config_data.conf_file)

        print(f"### {filename} ###\n") # Print here to help w/ debug

        conf = config_data.config
        if resolved:
            with read_write(conf):
                OmegaConf.resolve(conf)

        print(OmegaConf.to_yaml(conf))


@task(
#    positional=["config"],
    iterable=["config"],
)
def write(ctx,
          config=None,
          mkdir=True,
          write_all=False,
          overwrite=False,
          comment=True,
          output=None):
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
      output (default=None): The directory to write the output files to.
    """

    # Normalize arg for call
    if config == []:
        config = None

    Config.write_configs(
        config,
        mkdir=mkdir,
        write_all=write_all,
        overwrite=overwrite,
        comment=comment,
        out_dir=output,
    )

@task(
    iterable=["input"],
)
def install(ctx,
            input,
            symlink=True,
            overwrite=False,
            mkdir=True
):
    """
    Will install a set of config files into the default location.
    By default it will create symlinks in the config dir that point to the
    provided arguments.

    Files are disambiguated by name, so input filenames should match their
    expected names in the config dir.

    Arguments:
      input: One or more files to symlink/copy into config dir.
        A single directory as input can be used as shorthand for all the
        appropriately named files within it.
      symlink (default=True): Do we create a symlink pointing to the input
        file or simply copy the input into the config dir?
      overwrite (default=False): Do we overwrite existing files (creating
        backups as needed)? Otherwise, skip existing config files.
      mkdir (default=True): Do we create the config directories if needed?
    """

    # Normalize arg for call
    if input == []:
        raise RuntimeError("Must provide at least one input config.")

    Config.install_configs(
        inputs=input,
        symlink=symlink,
        overwrite=overwrite,
        mkdir=mkdir,
    )
