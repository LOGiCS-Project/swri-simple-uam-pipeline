"""
Various setup and development tasks for SimpleUAM Utility Modules.
"""


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
from invoke import task

PY_SRC_PATHS = (Path(_) for _ in ("src", "tests", "tasks.py"))
PY_SRC_LIST = tuple(str(_) for _ in PY_SRC_PATHS)
PY_SRC = " ".join(PY_SRC_LIST)

TESTING = os.environ.get("TESTING", "0") in {"1", "true"}
CI = os.environ.get("CI", "0") in {"1", "true", "yes", ""}
WINDOWS = os.name == "nt"
PTY = not WINDOWS and not CI

def _get_proj_root():
    """
    Searches parent directories for a config file directory.
    """
    dir_parts = list(Path(__file__).resolve().parts)
    while len(dir_parts) >= 1:
        root_dir = Path(*dir_parts)
        pyproj = root_dir / "pyproject.toml"
        src_dir = root_dir / "simple_uam"
        if (pyproj.exists()
            and pyproj.is_file()
            and src_dir.exists()
            and src_dir.is_dir()):
            return root_dir
        dir_parts = dir_parts[:-1]
    raise RuntimeError(
        f"Found no candidate project root dir in parents of {__file__}")

PROJ_ROOT = _get_proj_root()
CONF_DIR = PROJ_ROOT / "dev-config"

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

# def _latest(lines: List[str], regex: Pattern) -> Optional[str]:
#     for line in lines:
#         match = regex.search(line)
#         if match:
#             return match.groupdict()["version"]
#     return None

# def _unreleased(versions, last_release):
#     for index, version in enumerate(versions):
#         if version.tag == last_release:
#             return versions[:index]
#     return versions

# def _assert_proj_root(op: str):
#     if PROJ_ROOT.resolve() != Path.cwd().resolve():
#         raise RuntimeError(
#             f"{op} can only be run in project root dir at: {PROJ_ROOT}")

# def update_changelog(
#     inplace_file: str,
#     marker: str,
#     version_regex: str,
#     template_url: str,
# ) -> None:
#     """
#     Update the given changelog file in place.

#     Arguments:
#         inplace_file: The file to update in-place.
#         marker: The line after which to insert new contents.
#         version_regex: A regular expression to find currently documented versions in the file.
#         template_url: The URL to the Jinja template used to render contents.
#     """

#     _assert_proj_root("Update Changelog")

#     from git_changelog.build import Changelog
#     from git_changelog.commit import AngularStyle
#     from jinja2.sandbox import SandboxedEnvironment

#     AngularStyle.DEFAULT_RENDER.insert(0, AngularStyle.TYPES["build"])
#     env = SandboxedEnvironment(autoescape=False)
#     template_text = urlopen(template_url).read().decode("utf8")  # noqa: S310
#     template = env.from_string(template_text)
#     changelog = Changelog(".", style="angular")

#     if len(changelog.versions_list) == 1:
#         last_version = changelog.versions_list[0]
#         if last_version.planned_tag is None:
#             planned_tag = "0.1.0"
#             last_version.tag = planned_tag
#             last_version.url += planned_tag
#             last_version.compare_url = last_version.compare_url.replace("HEAD", planned_tag)

#     with open(inplace_file, "r") as changelog_file:
#         lines = changelog_file.read().splitlines()

#     last_released = _latest(lines, re.compile(version_regex))
#     if last_released:
#         changelog.versions_list = _unreleased(changelog.versions_list, last_released)
#     rendered = template.render(changelog=changelog, inplace=True)
#     lines[lines.index(marker)] = rendered

#     with open(inplace_file, "w") as changelog_file:  # noqa: WPS440
#         changelog_file.write("\n".join(lines).rstrip("\n") + "\n")


# @task
# def new_subpackage(c):
#     """
#     Creates a new subpackage dir.

#     Manually moving stuff around because
#     Copier's error recovery will clobber everything.
#     """

#     _assert_proj_root("New Subpackage")
#     raise RuntimeError("Needs updating for symlinks and new folder structure.")

#     temp_dir = tempfile.mkdtemp()
#     dist_file = 'dist_name.txt'
#     print(f"Unpacking template to: {temp_dir}")
#     copier.copy("subpackage-template",temp_dir,cleanup_on_error=False)

#     sub_dir = (Path(temp_dir) / dist_file).read_text()
#     target_dir = Path(__file__).parent /  sub_dir
#     print(f"Moving template to: {target_dir}")
#     shutil.move(temp_dir, target_dir)
#     (target_dir / dist_file).unlink()


# @task
# def check_dependencies(ctx):
#     """
#     Check for vulnerabilities in dependencies.

#     Arguments:
#         ctx: The context instance (passed automatically).
#     """

#     _assert_proj_root("Check Dependency Security")

#     # undo possible patching
#     # see https://github.com/pyupio/safety/issues/348
#     for module in sys.modules:  # noqa: WPS528
#         if module.startswith("safety.") or module == "safety":
#             del sys.modules[module]  # noqa: WPS420

#     importlib.invalidate_caches()

#     # reload original, unpatched safety
#     from safety.formatter import report
#     from safety.safety import check as safety_check
#     from safety.util import read_requirements

#     # retrieve the list of dependencies
#     requirements = ctx.run(
#         ["pdm", "export", "-f", "requirements", "--without-hashes"],
#         title="Exporting dependencies as requirements",
#         allow_overrides=False,
#     )

#     # check using safety as a library
#     def safety():  # noqa: WPS430
#         packages = list(read_requirements(StringIO(requirements)))
#         vulns = safety_check(packages=packages, ignore_ids="", key="", db_mirror="", cached=False, proxy={})
#         output_report = report(vulns=vulns, full=True, checked_packages=len(packages))
#         if vulns:
#             print(output_report)

#     ctx.run(safety, title="Checking dependencies")


# @task
# def check_docs(ctx):
#     """
#     Check if the documentation builds correctly.

#     Arguments:
#         ctx: The context instance (passed automatically).
#     """

#     _assert_proj_root("Check Documentation Formatting")

#     Path("htmlcov").mkdir(parents=True, exist_ok=True)
#     Path("htmlcov/index.html").touch(exist_ok=True)
#     ctx.run("mkdocs build -s", title="Building documentation", pty=PTY)

# @task
# def docs(ctx):
#     """
#     Build the documentation locally.

#     Arguments:
#         ctx: The context instance (passed automatically).
#     """

#     _assert_proj_root("Build Documentation")

#     ctx.run("mkdocs build", title="Building documentation")


# @task
# def docs_serve(ctx, host="0.0.0.0", port=8000):
#     """
#     Serve the documentation (localhost:8000).

#     Arguments:
#         ctx: The context instance (passed automatically).
#         host: The host to serve the docs from.
#         port: The port to serve the docs on.
#     """

#     _assert_proj_root("Run Documentation Server")

#     ctx.run(f"mkdocs serve -a {host}:{port}",
#             title="Serving documentation",
#             capture=False)


# @task
# def docs_deploy(ctx):
#     """
#     Deploy the documentation on GitHub pages.

#     Arguments:
#         ctx: The context instance (passed automatically).
#     """

#     _assert_proj_root("Deploy Documentation")

#     ctx.run("mkdocs gh-deploy", title="Deploying documentation")
