#!/usr/bin/env invoke

from invoke import task
import copier
import tempfile
import shutil
from pathlib import Path


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
