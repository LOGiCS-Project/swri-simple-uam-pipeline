"""
Various setup and development tasks for SimpleUAM Utility Modules.
"""

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
from invoke import task

PY_SRC_PATHS = list()
for src_dir in Path.cwd().iterdir():
    if src_dir.is_dir() and (src_dir / "__init__.py").exists():
        PY_SRC_PATHS.append(src_dir)

PY_SRC_LIST = tuple(str(_) for _ in PY_SRC_PATHS)
PY_SRC = " ".join(PY_SRC_LIST)

TESTING = os.environ.get("TESTING", "0") in {"1", "true"}
CI = os.environ.get("CI", "0") in {"1", "true", "yes", ""}
WINDOWS = os.name == "nt"
PTY = not WINDOWS and not CI
CONF_DIR = "config"

@task
def check_quality(ctx, files=PY_SRC):
    """
    Check that the code is well formatted (using flake8)

    Arguments:
        ctx: The context instance (passed automatically).
        files: The list of files to check, defaults to all '.py`
    """
    ctx.run(f"pdm run flake8 --config={CONF_DIR}/flake8.ini {files}")


@task  # noqa: WPS231
def check_types(ctx):  # noqa: WPS231
    """
    Check that the code is correctly typed.

    Arguments:
        ctx: The context instance (passed automatically).
    """
    # NOTE: the following code works around this issue:
    # https://github.com/python/mypy/issues/10633

    # compute packages directory path
    py = f"{sys.version_info.major}.{sys.version_info.minor}"
    pkgs_dir = Path("__pypackages__", py, "lib").resolve()

    # build the list of available packages
    packages = {}
    for package in pkgs_dir.glob("*"):
        if package.suffix not in {".dist-info", ".pth"} and package.name != "__pycache__":
            packages[package.name] = package

    # handle .pth files
    for pth in pkgs_dir.glob("*.pth"):
        with suppress(OSError):
            for package in Path(pth.read_text().splitlines()[0]).glob("*"):  # noqa: WPS440
                if package.suffix != ".dist-info":
                    packages[package.name] = package

    # create a temporary directory to assign to MYPYPATH
    with tempfile.TemporaryDirectory() as tmpdir:

        # symlink the stubs
        ignore = set()
        for stubs in (path for name, path in packages.items() if name.endswith("-stubs")):  # noqa: WPS335
            Path(tmpdir, stubs.name).symlink_to(stubs, target_is_directory=True)
            # try to symlink the corresponding package
            # see https://www.python.org/dev/peps/pep-0561/#stub-only-packages
            pkg_name = stubs.name.replace("-stubs", "")
            if pkg_name in packages:
                ignore.add(pkg_name)
                Path(tmpdir, pkg_name).symlink_to(packages[pkg_name], target_is_directory=True)

        # create temporary mypy config to ignore stubbed packages
        newconfig = Path(CONF_DIR, "mypy.ini").read_text()
        newconfig += "\n" + "\n\n".join(f"[mypy-{pkg}.*]\nignore_errors=true" for pkg in ignore)
        tmpconfig = Path(tmpdir, "mypy.ini")
        tmpconfig.write_text(newconfig)

        # set MYPYPATH and run mypy
        os.environ["MYPYPATH"] = tmpdir
        ctx.run(f"pdm run mypy --config-file {tmpconfig} {PY_SRC}")

@task(check_types, check_quality)
def check(ctx):
    """
    Runs both the type and code quality checkers.

    Arguments:
        ctx: The context instance (passed automatically).
    """
    pass

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

@task
def format(ctx):
    """
    Run formatting tools on the code.

    Arguments:
        ctx: The context instance (passed automatically).
    """
    ctx.run(
        f"pdm run autoflake -ir --exclude tests/fixtures --remove-all-unused-imports {PY_SRC}",
    )
    ctx.run(f"pdm run isort {PY_SRC}")
    ctx.run(f"pdm run black {PY_SRC}")


@task
def test(ctx, match=""):
    """
    Run the test suite.

    Arguments:
        ctx: The context instance (passed automatically).
        match: A pytest expression to filter selected tests.
    """
    py_version = f"{sys.version_info.major}{sys.version_info.minor}"
    os.environ["COVERAGE_FILE"] = f".coverage.{py_version}"
    ctx.run(f"pdm run pytest -c {CONF_DIR}/pytest.ini -n auto -k {repr(match)} tests")


@task
def coverage(ctx):
    """
    Report coverage as text and HTML.

    Arguments:
        ctx: The context instance (passed automatically).
    """
    ctx.run("pdm run coverage combine")
    ctx.run(f"pdm run coverage report --rcfile={CONF_DIR}/coverage.ini")
    ctx.run(f"pdm run coverage html --rcfile={CONF_DIR}/coverage.ini")

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
def docs_serve(ctx, host="0.0.0.0", port=8000):
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
