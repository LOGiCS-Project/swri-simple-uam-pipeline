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
from util.config import Config, PathConfig
import util.config.tasks
from util.invoke import task, Collection, InvokeProg
from util.logging import get_logger

log = get_logger(__name__)

@task
def test_logging(ctx):
    """
    A quick test of logging code.
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
            log.exception("poor me", ex = err)
        log.info("all better now!", stack_info=True)

    make_call_stack_more_impressive()

    log.info("done-now")



def main(args: Optional[List[str]] = None) -> int:
    """
    Run the main program.

    This function is executed when you type `simpleuam-utils` or `python -m util`.

    Arguments:
        args: Arguments passed from the command line.

    Returns:
        An exit code.
    """

    # Tasks initialized in this file
    tasks = Collection(
        test_logging,
    )

    # Import tasks from other files/modules
    namespace.add_collection(
        Collection.from_module(util.config.tasks),
        'config',
    )

    # Setup the invoke program runner class
    program = InvokeProg(
        namespace=tasks,
        version="0.1.0",
    )

    return program.run()

    # parser = get_parser()
    # opts = Config.get(PathConfig)
    # print(Config.configs())
    # print(Config.load_path(PathConfig))
    # print(OmegaConf.to_yaml(opts))  # noqa: WPS421 (side-effect in main is fine)
    return 0
