"""
Various setup and development tasks for SimpleUAM Utility Modules.
"""

import shutil
from simple_uam.util.invoke import task, call
from simple_uam.util.config import Config, PathConfig, CraidlConfig
from simple_uam.util.logging import get_logger

from simple_uam.craidl.corpus import GremlinCorpus, StaticCorpus, get_corpus
from simple_uam.craidl.info_files import DesignInfoFiles
from simple_uam.util.system import backup_file

from .examples import *
from pathlib import Path
import json

import subprocess

log = get_logger(__name__)

repo_data_corpus = Config[PathConfig].repo_data_dir / 'corpus_static_dump.json'

@task
def copy_static_corpus(ctx,
                       input = None,
                       output = None,
                       force = False,
                       backup = True):
    """
    Generates a static corpus from a running corpus server.

    Arguments:
      input: The input copy of the static corpus, defaults to the copy provided
        with the repo.
      output: The output file to write the corpus dump to. Defaults to the
        configured corpus location.
      force: Do we overwrite the corpus if it's already there? Defaults to
        true if output is specified otherwise defaults to false.
      backup: Should we create a backup if there's a preexisting output file?
    """

    if input == None:
        input = repo_data_corpus
    input = Path(input)

    if output == None:
        output = Config[CraidlConfig].static_corpus
    else:
        force = True
    output = Path(output)

    if output.exists() and not force:
        log.info(
            "Found existing corpus dump, skipping further operations.",
            output=str(output),
        )
        return
    elif output.exists() and backup:
        log.info(
            "Found existing corpus dump, creating backup and removing.",
            output=str(output),
        )
        backup_file(output, delete=True)
    elif output.exists():
        log.warning(
            "Found existing corpus dump, deleting.",
            output=str(output),
        )
        output.unlink()

    log.info(
        "Copying corpus data into location.",
        input_corpus = str(input),
        output_corpus = str(output),
    )
    shutil.copy2(input, output)

corpus_cache = Config[CraidlConfig].static_corpus_cache

corpus_cache_opts = 'corpus_options.json'

@task
def gen_static_corpus(ctx,
                      host = None,
                      port = None,
                      output = None,
                      force = False,
                      backup = True,
                      cache = True,
                      cache_dir = corpus_cache,
                      cluster_size = 100):
    """
    Generates a static corpus from a running corpus server.

    Arguments:
      host: The hostname of the server we connect to.
      port: The port we're connecting to the server on.
      output: The output file to write the corpus dump to.

    Secondary Arguments:
      force: Do we overwrite the corpus if it's already there? Defaults to
        true if output is specified otherwise defaults to false.
      backup: Should we create a backup if there's a preexisting output file?
      cache: Should we use a cache to generate this corpus?
      cache_dir: What directory should we use as a cache?
      cluster_size: If we're using a cache

    All three arguments will default to values from 'CraidlConfig' if not
    specified.
    """

    ### Normalize Args

    if host == None:
        host = Config[CraidlConfig].server_host

    if port == None:
        port = Config[CraidlConfig].server_port

    if output == None:
        output = Config[CraidlConfig].static_corpus
    else:
        force = True

    output = Path(output)
    cache_dir = Path(cache_dir)

    ### Clean Up Output Location

    if output.exists() and not force:
        log.info(
            "Found existing corpus dump, skipping further operations.",
            output=str(output),
        )
        return
    elif output.exists() and backup:
        log.info(
            "Found existing corpus dump, creating backup and removing.",
            output=str(output),
        )
        backup_file(output, delete=True)
    elif output.exists():
        log.warning(
            "Found existing corpus dump, deleting.",
            output=str(output),
        )
        output.unlink()

    ### Init cache

    corpus_opts = dict(
        host = host,
        port = port,
        cache_dir = str(cache_dir),
        cluster_size = cluster_size,
    )

    if cache:

        # Handle cases where cache was run with old options
        opts_file = cache_dir / corpus_cache_opts
        if opts_file.exists():
            log.info(
                "Found existing cache options, checking for match.",
                opts_file = str(opts_file),
            )
            delete_opts = False
            with opts_file.open('r') as of:
                old_opts = json.load(of)
                if old_opts != corpus_opts:
                    log.warning(
                        "Previous cache options were different from current "\
                        "options, deleting cache.",
                        opts_file=str(opts_file),
                        old_opts=old_opts,
                        curr_opts=corpus_opts,
                    )
                    delete_opts = True
            if delete_opts:
                shutil.rmtree(cache_dir, ignore_errors=True)

        # create new options file if needed
        cache_dir.mkdir(parents=True, exist_ok=True)
        if not opts_file.exists():
            log.info(
                "Creating new cache options file.",
                opts_file=str(opts_file),
                curr_opts = corpus_opts,
            )
            with opts_file.open('w') as of:
                json.dump(corpus_opts, of)

    ### Convert Corpus

    log.info(
        "Starting gremlin client.",
        host=host,
        port=port,
    )

    gremlin_corpus = GremlinCorpus(host=host, port=port)

    log.info(
        "Starting dump to static corpus.")

    static_corpus = StaticCorpus.from_corpus(
        gremlin_corpus,
        cache_dir = cache_dir if cache else None,
        cluster_size = cluster_size,
    )

    ### Output Corpus

    log.info(
        "Writing static corpus to file.",
        output=str(output),
    )

    with output.open('w') as fp:
        static_corpus.dump_json(fp)



@task
def gen_info_files(ctx,
                   design = 'design_swri.json',
                   output = None,
                   copy_design = False,
                   static = None,
                   host = None,
                   port = None):
    """
    Generates the info files for a given design.

    Arguments:
      design: '.json' with design information. Default: 'design_swri.json'
      output: The output **directory** in which to place the files.
        Default: cwd
      copy_design: Do we copy the input design to the output directory?
        Default: False

      static: The static '.json' corpus to use when generating the files.
        Mutually exclusive with host and port. Default: As configured
      host: The hostname of the corpus server to use when generating the files.
        Mutually exclusive with static. Default: As configured
      port: The port of the corpus server to use when generating the files.
        Mutually exclusice with static. Default: As configured
    """

    design = Path(design)

    if not output:
        output = Path.cwd()

    output = Path(output)

    corpus = get_corpus(static=static, host=host, port=port)

    log.info(
        "Loading designs from file.",
        design=str(design),
    )

    design_rep = None
    with design.open() as dp:
      design_rep = json.load(dp)

    log.info(
        "Generating info file data.",
    )

    info_files = DesignInfoFiles(corpus=corpus, design=design_rep)

    log.info(
        "Writing info files to disk.",
        output=str(output),
        copy_design=copy_design,
    )

    output.mkdir(parents=True, exist_ok=True)

    info_files.write_files(output)

    if copy_design:
        shutil.copy2(design, output / 'design_swri.json')
