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

def _latest(lines: List[str], regex: Pattern) -> Optional[str]:
    for line in lines:
        match = regex.search(line)
        if match:
            return match.groupdict()["version"]
    return None


def _unreleased(versions, last_release):
    for index, version in enumerate(versions):
        if version.tag == last_release:
            return versions[:index]
    return versions


def update_changelog(
    inplace_file: str,
    marker: str,
    version_regex: str,
    template_url: str,
) -> None:
    """
    Update the given changelog file in place.

    Arguments:
        inplace_file: The file to update in-place.
        marker: The line after which to insert new contents.
        version_regex: A regular expression to find currently documented versions in the file.
        template_url: The URL to the Jinja template used to render contents.
    """
    from git_changelog.build import Changelog
    from git_changelog.commit import AngularStyle
    from jinja2.sandbox import SandboxedEnvironment

    AngularStyle.DEFAULT_RENDER.insert(0, AngularStyle.TYPES["build"])
    env = SandboxedEnvironment(autoescape=False)
    template_text = urlopen(template_url).read().decode("utf8")  # noqa: S310
    template = env.from_string(template_text)
    changelog = Changelog(".", style="angular")

    if len(changelog.versions_list) == 1:
        last_version = changelog.versions_list[0]
        if last_version.planned_tag is None:
            planned_tag = "0.1.0"
            last_version.tag = planned_tag
            last_version.url += planned_tag
            last_version.compare_url = last_version.compare_url.replace("HEAD", planned_tag)

    with open(inplace_file, "r") as changelog_file:
        lines = changelog_file.read().splitlines()

    last_released = _latest(lines, re.compile(version_regex))
    if last_released:
        changelog.versions_list = _unreleased(changelog.versions_list, last_released)
    rendered = template.render(changelog=changelog, inplace=True)
    lines[lines.index(marker)] = rendered

    with open(inplace_file, "w") as changelog_file:  # noqa: WPS440
        changelog_file.write("\n".join(lines).rstrip("\n") + "\n")


@task
def changelog(ctx):
    """
    Update the changelog in-place with latest commits.

    Arguments:
        ctx: The context instance (passed automatically).
    """
    commit = "166758a98d5e544aaa94fda698128e00733497f4"
    template_url = f"https://raw.githubusercontent.com/pawamoy/jinja-templates/{commit}/keepachangelog.md"
    ctx.run(
        update_changelog,
        kwargs={
            "inplace_file": "CHANGELOG.md",
            "marker": "<!-- insertion marker -->",
            "version_regex": r"^## \[v?(?P<version>[^\]]+)",
            "template_url": template_url,
        },
        title="Updating changelog",
        pty=PTY,
    )

@task
def update_conda(c):
    """
    Updates conda environment from environment.yml
    """
    c.run("conda env update -f environment.yml")

@task
def new_subpackage(c):
    """
    Creates a new subpackage dir.

    Manually moving stuff around because
    Copier's error recovery will clobber everything.
    """

    temp_dir = tempfile.mkdtemp()
    dist_file = 'dist_name.txt'
    print(f"Unpacking template to: {temp_dir}")
    copier.copy("subpackage-template",temp_dir,cleanup_on_error=False)

    sub_dir = (Path(temp_dir) / dist_file).read_text()
    target_dir = Path(__file__).parent /  sub_dir
    print(f"Moving template to: {target_dir}")
    shutil.move(temp_dir, target_dir)
    (target_dir / dist_file).unlink()

@task
def check_dependencies(ctx):
    """
    Check for vulnerabilities in dependencies.

    Arguments:
        ctx: The context instance (passed automatically).
    """
    # undo possible patching
    # see https://github.com/pyupio/safety/issues/348
    for module in sys.modules:  # noqa: WPS528
        if module.startswith("safety.") or module == "safety":
            del sys.modules[module]  # noqa: WPS420

    importlib.invalidate_caches()

    # reload original, unpatched safety
    from safety.formatter import report
    from safety.safety import check as safety_check
    from safety.util import read_requirements

    # retrieve the list of dependencies
    requirements = ctx.run(
        ["pdm", "export", "-f", "requirements", "--without-hashes"],
        title="Exporting dependencies as requirements",
        allow_overrides=False,
    )

    # check using safety as a library
    def safety():  # noqa: WPS430
        packages = list(read_requirements(StringIO(requirements)))
        vulns = safety_check(packages=packages, ignore_ids="", key="", db_mirror="", cached=False, proxy={})
        output_report = report(vulns=vulns, full=True, checked_packages=len(packages))
        if vulns:
            print(output_report)

    ctx.run(safety, title="Checking dependencies")

@task
def check_docs(ctx):
    """
    Check if the documentation builds correctly.

    Arguments:
        ctx: The context instance (passed automatically).
    """
    Path("htmlcov").mkdir(parents=True, exist_ok=True)
    Path("htmlcov/index.html").touch(exist_ok=True)
    ctx.run("mkdocs build -s", title="Building documentation", pty=PTY)

@task
def docs(ctx):
    """
    Build the documentation locally.

    Arguments:
        ctx: The context instance (passed automatically).
    """
    ctx.run("mkdocs build", title="Building documentation")


@task
def docs_serve(ctx, host="127.0.0.1", port=8000):
    """
    Serve the documentation (localhost:8000).

    Arguments:
        ctx: The context instance (passed automatically).
        host: The host to serve the docs from.
        port: The port to serve the docs on.
    """
    ctx.run(f"mkdocs serve -a {host}:{port}", title="Serving documentation", capture=False)


@task
def docs_deploy(ctx):
    """
    Deploy the documentation on GitHub pages.

    Arguments:
        ctx: The context instance (passed automatically).
    """
    ctx.run("mkdocs gh-deploy", title="Deploying documentation")

@task(silent=True)
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
