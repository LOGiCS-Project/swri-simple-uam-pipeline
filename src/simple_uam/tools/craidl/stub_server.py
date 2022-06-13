"""
Various setup and development tasks for SimpleUAM Utility Modules.
"""

import shutil
from simple_uam.util.invoke import task, call
from simple_uam.util.config import Config, PathConfig, CraidlConfig
from simple_uam.util.logging import get_logger
from simple_uam.util.system import Git, configure_file, backup_file
from simple_uam.util.system.windows import download_file, verify_file, unpack_file, \
    run_gui_exe, append_to_file, get_mac_address
from pathlib import Path
import tempfile
import subprocess

log = get_logger(__name__)

uav_workflows_dir = Path(Config[CraidlConfig].stub_server.cache_dir) / 'uav_workflows'

uav_workflows_repo = "https://git.isis.vanderbilt.edu/SwRI/athens-uav-workflows.git"

uav_workflows_branch = "uam_corpus"

uav_workflows_corpus = uav_workflows_dir / 'ExportedGraphML' / 'all_schema_uam.graphml'

@task
def download_corpus(ctx,  prompt=True, quiet=False, verbose=False):
    """
    Downloads the repo which has the default stub server corpus and saves it
    to an appropriate cache directory.

    Arguments:
      prompt: Prompt for a password on initial git clone.
      quiet: Run in quiet mode.
      verbose: Run in verbose mode.
    """

    git_args = dict(
        repo_uri = uav_workflows_repo,
        deploy_dir = str(uav_workflows_dir),
        branch = uav_workflows_branch,
        password_prompt = prompt,
        quiet = quiet,
        verbose = verbose,
        mkdir = True
    )

    if not quiet:
        log.info("Running git clone/pull for uav-workflows.",**git_args)

    Git.clone_or_pull(**git_args)

@task
def install_corpus(ctx, corpus=None, skip=False, yes=False):
    """
    Install the stub server corpus into the configured location.

    Arguments:
      corpus: The '.graphml' file to generate the corpus from, defaults to the
        file from the download step if found.
      skip: skip updating corpus if existing corpus is found.
      yes: skip confirmation prompt if old corpus is deleted.
    """

    # Default

    if not corpus:
        download_corpus(ctx)
        corpus = uav_workflows_corpus
    else:
        corpus = Path(corpus)

    # Input Checks

    if not corpus.is_file():
        err = RuntimeError("Corpus file does not exist.")
        log.exception(
            "Could not find corpus file in the following location.",
            corpus_file = str(corpus),
        )
        raise err

    if corpus.suffix != ".graphml":
        err = RuntimeError("Corpus file must be '.graphml' format.")
        log.exception(
            "Corpus file ",
            corpus_file = str(corpus),
        )
        raise err

    # Output Checks

    target = Path(Config[CraidlConfig].stub_server.graphml_corpus)

    if target.exists() and skip:
        log.info(
            "Corpus already exists at target location, skipping update.",
            target = target,
        )
        return
    elif target.exists() and not yes:
        log.warning(
            "Corpus already exists at target location, delete?",
            target = target,
        )
        choice = input("Confirm deletion (y/N):")

        if choice != 'y':
            raise RuntimeError("Confirmation not given, aborting.")

        target.unlink()

    target.parent.mkdir(parents=True, exist_ok=True)

    # Copying

    log.info(
        "Copying stub-server corpus to target location.",
        corpus = str(corpus),
        target = str(target),
    )

    shutil.copy2(corpus, target)

gremlin_server_uri = "https://downloads.apache.org/tinkerpop/3.6.0/apache-tinkerpop-gremlin-server-3.6.0-bin.zip"

gremlin_server_zip = Path(Config[CraidlConfig].stub_server.cache_dir) / 'gremlin-server-3.6.0.zip'

gremlin_unpack_folder = "apache-tinkerpop-gremlin-server-3.6.0"

gremlin_server_dir = Path(Config[CraidlConfig].stub_server.server_dir)

gremlin_server_md5 = "EB7FC24DDC886CF38A2D972F7688C574"

gremlin_server_cmd = Path('bin','gremlin-server.bat')

@task
def download_server(ctx, force_download=False):
    """
    Downloads, and the gremlin server stub.

    Arguments:
      force_download: Download even if the archive is already there.
    """

    gremlin_server_zip.parent.mkdir(parents=True, exist_ok=True)

    if gremlin_server_zip.exists():
        if force_download:
            log.info(
                "Archive exists with force download flag set. Deleting.",
                zip_file = str(gremlin_server_zip),
            )
            gremlin_server_zip.unlink()
        elif gremlin_server_md5:
            log.info(
                "Found existing zip for the gremlin_server, validating hash.",
                zip_file = str(gremlin_server_zip),
                md5_hash = gremlin_server_md5,
            )
            if not verify_file(gremlin_server_zip, gremlin_server_md5):
                log.warning("Server zip is broken redownloading.")
                gremlin_server_zip.unlink()

    if gremlin_server_zip.exists():
        log.info(
            "Server archive is already downloaded.",
            archive=str(gremlin_server_zip),
        )
    else:
        log.info(
            "No archive found, downloading now.",
            archive=str(gremlin_server_zip),
            download_uri=gremlin_server_uri,
        )
        download_file(gremlin_server_uri, gremlin_server_zip)

@task
def unpack_server(ctx, force_unpack=False, force_download=False):
    """
    Unpacks the gremlin server archive into its final location.

    Arguments:
       force_unpack: Will delete the current server dir before unpacking.
       force_download: Will force a redownload of the server archive, implies
         force_unpack.
    """

    force_unpack = force_unpack or force_download

    download_server(ctx, force_download=force_download)

    gremlin_server_dir.parent.mkdir(parents=True, exist_ok=True)

    if gremlin_server_dir.exists() and force_unpack:
        log.info(
            "Server dir already exists but force unpack is set. Deleting.",
            server_dir = str(gremlin_server_dir),
        )
        shutil.rmtree(gremlin_server_dir)

    if gremlin_server_dir.exists():
        log.info(
            "Server dir already exists skipping unpack.",
            server_dir = str(gremlin_server_dir),
        )
    else:
        log.info(
            "Server dir not found, unpacking zip now.",
            server_zip = str(gremlin_server_zip),
            server_dir = str(gremlin_server_dir),
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            unpack_file(gremlin_server_zip, temp_dir)
            gremlin_unpack_dir = Path(temp_dir) / gremlin_unpack_folder
            shutil.move(gremlin_unpack_dir, gremlin_server_dir)

conf_data_root = Config[PathConfig].repo_dir / 'data' / 'gremlin-server'

server_conf_data = conf_data_root / 'gremlin-server-uam.yaml'
server_conf_target = Path('conf','gremlin-server-uam.yaml')
server_conf_path = gremlin_server_dir / server_conf_target

corpus_loader_data = conf_data_root / 'uam-corpus.groovy'
corpus_loader_target = Path('scripts','uam-corpus.groovy')
corpus_loader_path = gremlin_server_dir / corpus_loader_target

corpus_data_target = Path('data', 'all_schema_uam.graphml')
corpus_data_path = gremlin_server_dir / corpus_data_target

@task(unpack_server)
def configure_server(ctx,
                     host = None,
                     port = None,
                     corpus = None):
    """
    Will patch the stub server's config files and copy over the corpus if
    needed.

    Arguments:
      host: The host the server will serve on.
      port: The port the server will server on.
      corpus: The '.graphml' file to be loaded whenever the server starts.

    All three arguments will default to values from 'CraidlConfig's
    'stub_server' entry.
    """

    # Defaults

    if not host:
        host = Config[CraidlConfig].stub_server.host

    if not port:
        port = Config[CraidlConfig].stub_server.port

    if not corpus:
        install_corpus(ctx, skip=True)
        corpus = Path(Config[CraidlConfig].stub_server.graphml_corpus)
    else:
        corpus = Path(corpus)

    ## Server Conf

    configure_file(
        server_conf_data,
        server_conf_path,
        replacements = {
            '<<HOSTNAME>>': host,
            '<<PORT>>': str(port),
            '<<LOAD_SCRIPT>>': corpus_loader_target.as_posix(),
        },
        exist_ok = True,
    )

    ## Corpus Loader

    read_only = Config[CraidlConfig].stub_server.read_only
    traversal_strats = 'ReadOnlyStrategy' if read_only else ''

    configure_file(
        corpus_loader_data,
        corpus_loader_path,
        replacements = {
            '<<CORPUS_DATA>>': corpus_data_target.as_posix(),
            '<<TRAVERSAL_STRATEGIES>>': traversal_strats,
        },
        exist_ok = True,
    )

    ## Corpus schema

    if corpus_data_path.is_symlink():
        log.info(
            "Unlinking corpus data symlink.",
            corpus_link=str(corpus_data_path),
        )
        corpus_data_path.unlink()
    elif corpus_data_path.is_file():
        log.warning(
            "Corpus file exists and isn't symlink, moving to backup.",
            corpus_file=str(corpus_data_path),
        )
        backup_file(
            corpus_data_path,
            delete=True,
        )

    log.info(
        "Creating corpus symlink.",
        src=corpus,
        dest=str(corpus_data_path),
    )
    corpus_data_path.symlink_to(corpus)

@task
def run_server(ctx):
    """
    Runs the stub server with the configured settings. This does not run the
    server as a service, it's just in the current session.
    """

    cmd = (gremlin_server_dir / gremlin_server_cmd).resolve()

    log.info(
        "Starting gremlin stub server.",
        cmd=str(cmd),
        conf=str(server_conf_target),
        cwd=str(gremlin_server_dir),
    )

    subprocess.run(
        [cmd, server_conf_target],
        cwd = gremlin_server_dir,
    )
