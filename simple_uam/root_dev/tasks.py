#!/usr/bin/env invoke

from invoke import task
import copier
import tempfile
import shutil
import os
import re
import sys
from contextlib import suppress
from io import StringIO
from pathlib import Path
from typing import List, Optional, Pattern
from urllib.request import urlopen
from pathlib import Path

PY_SRC_PATHS = (Path(_) for _ in ("src", "tests", "duties.py", "docs"))
PY_SRC_LIST = tuple(str(_) for _ in PY_SRC_PATHS)
PY_SRC = " ".join(PY_SRC_LIST)
TESTING = os.environ.get("TESTING", "0") in {"1", "true"}
CI = os.environ.get("CI", "0") in {"1", "true", "yes", ""}
WINDOWS = os.name == "nt"
PTY = not WINDOWS and not CI

@task
def check_docs(ctx):
    """
    Check if the documentation builds correctly.

    Arguments:
        ctx: The context instance (passed automatically).
    """
    Path("htmlcov").mkdir(parents=True, exist_ok=True)
    Path("htmlcov/index.html").touch(exist_ok=True)
    ctx.run("pdm run mkdocs build -s")

@task
def docs(ctx):
    """
    Build the documentation locally.

    Arguments:
        ctx: The context instance (passed automatically).
    """
    ctx.run("pdm run mkdocs build")

@task
def docs_serve(ctx, host="127.0.0.1", port=8000):
    """
    Serve the documentation (localhost:8000).

    Arguments:
        ctx: The context instance (passed automatically).
        host: The host to serve the docs from.
        port: The port to serve the docs on.
    """
    ctx.run(f"pdm run mkdocs serve -a {host}:{port}")


@task
def docs_deploy(ctx):
    """
    Deploy the documentation on GitHub pages.

    Arguments:
        ctx: The context instance (passed automatically).
    """
    ctx.run("pdm run mkdocs gh-deploy")

@task
def clean(ctx):
    """
    Delete temporary files.

    Arguments:
        ctx: The context instance (passed automatically).
    """
    ctx.run("rm -rfv .coverage*")
    ctx.run("rm -rfv .mypy_cache")
    ctx.run("rm -rfv .pytest_cache")
    ctx.run("rm -rfv tests/.pytest_cache")
    ctx.run("rm -rfv build")
    ctx.run("rm -rfv dist")
    ctx.run("rm -rfv htmlcov")
    ctx.run("rm -rfv pip-wheel-metadata")
    ctx.run("rm -rfv site")
    ctx.run("find . -type d -name __pycache__ | xargs rm -rf")
    ctx.run("find . -name '*.rej' -delete")

@task(clean)
def reset_pdm(ctx):
    """
    Delete all local pdm install files.

    Arguments:
        ctx: The context instance (passed automatically).
    """
    ctx.run("rm -rfv pdm.lock .pdm.toml __pypackages__")
