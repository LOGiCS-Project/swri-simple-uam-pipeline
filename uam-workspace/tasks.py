"""
Various setup and development tasks for UAM Workspace.
"""

import os
import sys
import tempfile
from contextlib import suppress
from pathlib import Path

from invoke import task

PY_SRC_PATHS = (Path(_) for _ in ("src", "tests", "tasks.py"))
PY_SRC_LIST = tuple(str(_) for _ in PY_SRC_PATHS)
PY_SRC = " ".join(PY_SRC_LIST)

@task
def setup(ctx):
    """
    Sets up the subproject using `pdm install -d`.
    Will also process changes to `pyproject.toml`.

    Arguments:
        ctx: The context instance (passed automatically).
    """
    ctx.run("pdm install -d")

@task
def check_quality(ctx, files=PY_SRC):
    """
    Check that the code is well formatted (using flake8)

    Arguments:
        ctx: The context instance (passed automatically).
        files: The list of files to check, defaults to all '.py`
    """
    ctx.run(f"pdm run flake8 --config=config/flake8.ini {files}")

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
        newconfig = Path("config", "mypy.ini").read_text()
        newconfig += "\n" + "\n\n".join(f"[mypy-{pkg}.*]\nignore_errors=true" for pkg in ignore)
        tmpconfig = Path(tmpdir, "mypy.ini")
        tmpconfig.write_text(newconfig)

        # set MYPYPATH and run mypy
        os.environ["MYPYPATH"] = tmpdir
        ctx.run(f"pdm run mypy --config-file {tmpconfig} {PY_SRC}")

@task(pre=["check_types","check_quality"])
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
    ctx.run("rm -rf .coverage*")
    ctx.run("rm -rf .mypy_cache")
    ctx.run("rm -rf .pytest_cache")
    ctx.run("rm -rf tests/.pytest_cache")
    ctx.run("rm -rf build")
    ctx.run("rm -rf dist")
    ctx.run("rm -rf htmlcov")
    ctx.run("rm -rf pip-wheel-metadata")
    ctx.run("rm -rf site")
    ctx.run("find . -type d -name __pycache__ | xargs rm -rf")
    ctx.run("find . -name '*.rej' -delete")


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
def test(ctx, match = ""):
    """
    Run the test suite.

    Arguments:
        ctx: The context instance (passed automatically).
        match: A pytest expression to filter selected tests.
    """
    py_version = f"{sys.version_info.major}{sys.version_info.minor}"
    os.environ["COVERAGE_FILE"] = f".coverage.{py_version}"
    ctx.run(
        f"pdm run pytest -c config/pytest.ini -n auto -k {repr(match)} tests"
    )

@task
def coverage(ctx):
    """
    Report coverage as text and HTML.

    Arguments:
        ctx: The context instance (passed automatically).
    """
    ctx.run("pdm run coverage combine")
    ctx.run("pdm run coverage report --rcfile=config/coverage.ini")
    ctx.run("pdm run coverage html --rcfile=config/coverage.ini")