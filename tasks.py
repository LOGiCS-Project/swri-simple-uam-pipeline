#!/usr/bin/env invoke

from invoke import task
import copier

@task
def update_conda(c):
    c.run("conda env update -f environment.yml")

@task
def new_subpackage(c):
    copier.copy("subpackage-template",".",cleanup_on_error=False)
