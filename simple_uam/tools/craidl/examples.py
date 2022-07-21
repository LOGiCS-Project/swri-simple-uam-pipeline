"""
Various setup and development tasks for SimpleUAM Utility Modules.
"""

import shutil
from simple_uam.util.invoke import task, call
from simple_uam.util.config import Config, PathConfig, CraidlConfig, \
    AuthConfig, CorpusConfig
from simple_uam.util.logging import get_logger
from simple_uam.util.system import Git
from simple_uam.craidl.corpus import GremlinCorpus, StaticCorpus, get_corpus
from simple_uam.craidl.designs import GremlinDesignCorpus, StaticDesignCorpus

from typing import Tuple

from pathlib import Path

import tempfile
import json
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

    for name, design_file in all_examples().items():
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
                example.rmdir()
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

@task
def add_examples(ctx, input=None, name=None, skip=False):
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

    if not input:
        raise RuntimeError("Please specify example file or directory.")

    examples = dict()
    input_loc = Path(input).resolve(strict=True)

    log.info(
        "Attempting to add examples from input.",
        input=input,
    )

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
        for example in input_loc.glob(f'*/{design_filename}'):
            name = example.parent.name
            examples[name] = example

    for name, design in examples.items():
        target_dir = example_path / name
        target_file = target_dir / design_filename

        target_dir.mkdir(parents=True, exist_ok=True)

        if not target_file.exists():
            log.info(
                "Example does not exist, installing.",
                name=name,
                source=str(design),
                destination=str(target_file),
            )
            shutil.copy2(design, target_file)
        elif not skip:
            log.warning(
                "Example already exists, deleting and reinstalling.",
                name=name,
                source=str(design),
                destination=str(target_file),
            )
            target_file.unlink()
            shutil.copy2(design, target_file)
        else:
            log.info(
                "Example already exists, skipping.",
                name=name,
                source=str(design),
                destination=str(target_file),
            )

trinity_craidl_dir = Config[PathConfig].cache_dir / 'trinity_craidl'

trinity_craidl_repo = Config[CorpusConfig].trinity.repo

trinity_craidl_branch = Config[CorpusConfig].trinity.branch

trinity_craidl_examples = trinity_craidl_dir / Config[CorpusConfig].trinity.examples_dir

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
        deploy_dir = str(trinity_craidl_dir),
        remote_user = Config[AuthConfig].isis_user,
        remote_pass = Config[AuthConfig].isis_token,
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

@task(pre=[download_examples, call(add_examples,input=trinity_craidl_examples)])
def install_examples(ctx):
    """
    Installs the trinity-craidl examples after, possibly, downloading them.
    """
    log.info(
        "Installed examples from trinity-craidl repo."
    )

@task
def list_examples(ctx):
    """
    Lists all currently loaded examples.
    """

    for name, path in all_examples().items():
        print(f"{name}:  {str(path)}")

@task
def examples_dir(ctx):
    """
    Print the current examples directory.
    """
    print(str(example_path))


@task
def list_corpus_db_examples(ctx,
                            host = None,
                            port = None):
    """
    Lists the designs that are on a corpus DB

    Arguments:
      host: The hostname of the server we connect to.
      port: The port we're connecting to the server on.

    All arguments will default to values from 'CraidlConfig' if not
    specified.
    """

    ### Normalize Args

    if host == None:
        host = Config[CraidlConfig].server_host

    if port == None:
        port = Config[CraidlConfig].server_port

    design_corpus = GremlinDesignCorpus(host=host, port=port)

    try:
        for design_name in design_corpus.designs:
            print(design_name)
    finally:
        design_corpus.close()

@task(iterable=['name'])
def install_corpus_db_examples(ctx,
                               name = None,
                               host = None,
                               port = None):
    """
    Lists the designs that are on a corpus DB

    Arguments:
      name: Name of the example to download, defaults to all.
      host: The hostname of the server we connect to.
      port: The port we're connecting to the server on.

    `host` and `port` will default to values from 'CraidlConfig' if not
    specified.
    """

    if host == None:
        host = Config[CraidlConfig].server_host

    if port == None:
        port = Config[CraidlConfig].server_port

    design_corpus = GremlinDesignCorpus(host=host, port=port)

    try:
        examples = name

        if not examples:
            log.info("Getting list of examples from DB")
            examples = design_corpus.designs

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_dir = Path(tmp_dir)
            tmp_dir.mkdir(parents=True, exist_ok=True)

            for example in examples:
                log.info(f"Reading {example} from DB")
                design_rep = design_corpus[example].rendered()

                tmp_file = tmp_dir / f"{example}.json"
                tmp_file.unlink(missing_ok=True)

                with tmp_file.open("w") as tmp:
                    json.dump(design_rep, tmp, indent="  ")

                add_examples(
                    ctx,
                    input=tmp_file,
                    name=example,
                )
    finally:
        design_corpus.close()
