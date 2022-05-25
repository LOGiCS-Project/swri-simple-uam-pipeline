# Why does this file exist, and why not put this in `__main__`?
#
# You might be tempted to import things from `__main__` later,
# but that will cause problems: the code will get executed twice:
#
# - When you run `python -m uam_worker` python will execute
#   `__main__.py` as a script. That means there won't be any
#   `uam_worker.__main__` in `sys.modules`.
# - When you import `__main__` it will get executed again (as a module) because
#   there's no `uam_worker.__main__` in `sys.modules`.

"""Module that contains the command line application."""

import argparse
from typing import List, Optional
from util.invoke import task, Collection, InvokeProg

from util.config import Config, PathConfig
from .config import *
import util.config.tasks

from util.logging import get_logger

log = get_logger(__name__)

@task
def task_example(ctx, arg):
    """
    An example task with one argument. (see docstring for more info)

    This docstring will be visible under:
      - `uam-worker task-example --help`.

    See https://www.pyinvoke.org/ for details on how to use the `@task` decorator
    and how to setup a command line app.
    """

    print(f"Example Task: {arg}")

@task
def logging_example(ctx):
    """
    A quick test of logging code. (see docstring for more info)

    To use the logging capability, include the following near the start of each
    module:

    ```
    from util.logging import get_logger

    log = get_logger(__name__)
    ```

    From then on, you can use `log` to write information out to STDOUT, as below.
    Logging to file and command-line logging options will come if there's a specific
    need for them.

    Logging is done with structlog and mostly default settings.
    See this for the basic interface:
      - https://www.structlog.org/en/stable/api.html#structlog.PrintLogger
    """

    log.debug("debugging is hard", a_list=[1, 2, 3])
    log.info("informative!", some_key="some_value")
    log.warning("uh-uh!")
    log.error("omg", a_dict={"a": 42, "b": "foo"})
    log.critical("wtf")

    def make_call_stack_more_impressive():
        try:
            d = {"x": 42}
            print(SomeClass(d["y"], "foo"))
        except Exception as err:
            log.exception("poor me", ex=err)
        log.info("all better now!", stack_info=True)

    make_call_stack_more_impressive()

    log.info("done-now")

@task
def config_example(ctx):
    """
    Example config file usage.
    """

    log.info(
        """
        Config files are defined using config dataclasses, see `config/dataclass.py`
        that specify their fields and defaults.

        In order to use/see a config class it must be imported either directly or
        indirectly. From there, access the data via the `Config` object.
        """,
        desc_1= "Accessing config using `.get`",
        code_1="Config.get(PathConfig)",
        result_1=Config.get(PathConfig),
        desc_2= "Accessing config using lookup notation",
        code_2="Config[UAMWorkerConfig]",
        result_2=Config[UAMWorkerConfig],
    )

    log.info(
        "Fields within the config object work just like fields in a dataclass.",
        code_1="Config.get(PathConfig).config_dir",
        result_1=Config.get(PathConfig).config_dir,
        code_2="Config[UAMWorkerConfig].example_str",
        result_2=Config[UAMWorkerConfig].example_str,
    )

    log.info(
        f"""
        The config system will load config files based on the current load path,
        a list of directories that are checked in order for approprite config files.

        The load path starts off with:
          - {Config().config_dirs[0]}

        If there's a `paths.conf.yaml` file in that directory with a `config_dir`
        specified it adds that to load path, repeating until done.

        Then any directories specified using the `--config-dir=...` command line
        option are added to the load path.

        Current Load Path:
        """,
        load_path = [str(d) for d in Config().config_dirs],
    )

    log.info(
        """
        With a load path, the config system then looks at the `--run-mode=..` flag.
        If its there, it adds the subdirectory for each run-mode to the search path.

        So if "conf_dir/" is on the load_path and "--run-mode=production" is
        specified, the config system will search for files in "conf_dir/" and then
        "conf_dir/production".

        Note that settings towards the end of the load path override settings
        from earlier entries.

        The current load paths for PathConfig and UAMWorkerConfig:
        """,
        path=[str(p) for p in Config.load_path(PathConfig)],
        uam_worker=[str(p) for p in Config.load_path(UAMWorkerConfig)],
    )

    log.info(
        """
        You can further examine the current config state with tasks from the
        `util.config.tasks` module.

        The three basic tasks will give you information about all available
        configs:
          - `uam-worker config.classes` : List all config class names.
          - `uam-worker config.keys` : List all config interpolation keys.
          - `uam-worker config.files` : List the different config file names.

       The various strings returned by the above commands can be used to specify
       the config classes you're interested in for the other commands:
          - `uam-worker config.path` : Print the load path
            for a config class.
          - `uam-worker config.print` : Print the currently
            loaded data for a config class in YAML format.
          - `uam-worker config.write` : Write the currently
            loaded config data to the appropriate file.

       The help system contains more information:
          - `uam-worker --help [subcommand]`
       """
    )

def main(args: Optional[List[str]] = None) -> int:
    """
    Run the main program.

    This function is executed when you type `uam-worker` or `python -m uam_worker`.

    Arguments:
        args: Arguments passed from the command line.

    Returns:
        An exit code.
    """


    # Tasks in the top level namespace
    namespace = Collection(
        task_example,
        logging_example,
        config_example,
    )

    # Import tasks from other files/modules
    namespace.add_collection(
        Collection.from_module(util.config.tasks),
        'config',
    )

    # Setup the invoke program runner class
    program = InvokeProg(
        namespace=namespace,
        version="0.1.0",
    )

    return program.run()
