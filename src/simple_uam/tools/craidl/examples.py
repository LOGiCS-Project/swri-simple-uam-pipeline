"""
Various setup and development tasks for SimpleUAM Utility Modules.
"""

import shutil
from simple_uam.util.invoke import task, call
from simple_uam.util.config import Config, PathConfig, CraidlConfig
from simple_uam.util.logging import get_logger

from typing import Tuple

from pathlib import Path

import random
import subprocess

log = get_logger(__name__)

example_path = Path(Config[CraidlConfig].example_dir).resolve()

design_filename = 'design_swri.json'

def all_examples():
    """
    Returns a map of all examples from the example directory.
    """

    examples = dict()

    for example in example_path.glob(f'*/{design_filename}'):
        name = example.parent.name
        examples[name] = example

    return examples

def random_example() -> Tuple[str,Path]:
    """
    Returns a random example from the example directory.
    """

    examples = list(all_examples().items())

    if len(examples) == 0:
        raise RuntimeError("No design examples installed to choose from.")

    return random.choice(examples)

def match_example(ident, random=False) -> Tuple[str,Path]:
    """
    Returns the first example from the example dir which has 'ident' as a
    substring.

    Arguments:
      ident: the identifier substring
      random: return a random ex
    """

    for name, file in all_examples():
        if ident in name:
            return tuple(name, file)

    if random:
        return random_example()
    else:
        err = RuntimeError("Could not find design example with matching ident.")
        log.exception(
            "No matching example found in available identifiers.",
            err = err,
            ident = ident,
            availabe = list(all_examples.keys())
        )
        raise err

@task
def clean_examples(ctx):
    """
    Deletes all available examples in the default directory.
    """

    example_path.mkdir(parents=True, exist_ok=True)

    for name, design_file in all_examples():
        design_file = design_file.resolve()

        log.info(
            "Deleting example design.",
            name = name,
            design_file = str(design_file),
        )
        design_file.unlink()

    for example in example_path.iterdir():
        if example.is_dir():
            if sum(1 for _ in example.iterdir()) == 0:
                log.info(
                    "Deleting example directory.",
                    design_dir = str(example),
                )
                design_dir.rmdir()
            else:
                log.warning(
                    "Example design directory still has items, skipping deletion.",
                    design_dir = str(example),
                )
        else:
            log.warning(
                "File found in example directory, skipping deletion.",
                file = str(example),
            )

@task(positional=["input"])
def add_examples(ctx, input, name=None, skip=False):
    """
    Adds the given example(s) to the examples dir.

    Arguments:
      input: If a directory this will copy over all the 'design_swri.json'
        files in subdirectories ('*/design_swri.json') with the parent dir
        used as an example name. See 'name' for when input is a file.
      name: The name of the example to use when copying over the single file
        example.
      skip: skips any examples that already exist with the same name, otherwise
        overwrites them.
    """

    examples = dict()
    input_loc = Path(input).resolve(strict=True)

    if input_loc.is_file() and not name:
        err = RuntimeError("Need name argument for single fine input.")
        log.exception(
            "Provided input file, rather than dir, and no name.",
            input = input,
            name = name,
        )
        raise err
    elif input_loc.is_file():
        examples[name] = input_loc
    else:
        examples = all_examples()

    for name, design in examples.items():
        target_dir = example_path / name
        target_file = target_dir / design_filename

        target_dir.mkdir(parents=True, exist_ok=True)

        if not target_file.exists():
            log.info(
                "Example does not exist, installing.",
                name=name,
                source=design,
                destination=target_file,
            )
            shutil.copy2(design, target_file)
        elif not skip:
            log.info(
                "Example already exists, deleting and reinstalling.",
                name=name,
                source=design,
                destination=target_file,
            )
            target_file.unlink()
            shutil.copy2(design, target_file)
        else:
            log.info(
                "Example already exists, skipping.",
                name=name,
                source=design,
                destination=target_file,
            )

trinity_craidl_dir = Config[PathConfig].cache_path / 'trinity_craidl'

trinity_craidl_repo = "https://git.isis.vanderbilt.edu/SwRI/ta1/sri-ta1/trinity-craidl.git"

trinity_craidl_branch = "main"

trinity_craidl_examples = trinity_craidl_dir / 'examples'

@task
def download_examples(ctx,  prompt=True, quiet=False, verbose=False):
    """
    Clones the trinity-craidl repo into the appropriate folder. With a default
    config this makes the examples available for use with other options.

    Arguments:
      prompt: Prompt for a password on initial git clone.
      quiet: Run in quiet mode.
      verbose: Run in verbose mode.
    """

    git_args = dict(
        repo_uri = trinity_craidl_repo,
        deploy_dir = trinity_craidl_dir,
        branch = trinity_craidl_branch,
        password_prompt = prompt,
        quiet = quiet,
        verbose = verbose,
        mkdir = True
    )

    if not quiet:
        log.info("Running git clone/pull for trinity-craidl design examples."
                 ,**git_args)

    Git.clone_or_pull(**git_args)

@task(download_examples, call(add_examples, trinity_craidl_examples))
def install_examples(ctx):
    """
    Installs the trinity-craidl examples after, possibly, downloading them.
    """
    pass
