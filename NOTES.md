# Notes for future development

Assorted notes for development

## Setup Notes

  - `conda env create -f environment.yml`
  - `conda activate simple-uam`

## Tasks

  - Update conda env:
      - In repo root & conda env: `invoke update`

## Library Use

  - [platformdirs](https://pypi.org/project/platformdirs/) : For finding
    appropriate local config and working directories.
  - [pdm](https://pdm.fming.dev/) : Python build and dep management tool like
    poetry or pipenv. (Except it doesn't choke when a package author forgets
    a metadata field)
  - [invoke](https://docs.pyinvoke.org/en/stable/) : To act as a CLI interface
    wrapper for setup and evaluation.
  <!-- - [duty](https://pawamoy.github.io/duty/) : A task runner for cli -->
  - [omegaconf](https://omegaconf.readthedocs.io) : Just basic config opts
  <!-- - [hydra](https://hydra.cc/) : For storing and generating hierarchical configs -->
  <!-- - [dynaconf](https://www.dynaconf.com/validation/) : for config management -->
  <!--   and parsing -->
  - [structlog](https://www.structlog.org/en/stable/loggers.html) : for good
    logging
  <!-- - [coloredlogs](https://pypi.org/project/coloredlogs/) : For pretty logs -->
  - [attrs](https://www.attrs.org/en/stable/) : For minimizing boilerplate and
    sensible dataclasses.
  - [celery](https://docs.celeryq.dev) : For managing worker/customer
    interactions.
      - Use `add_defaults` to tie the knot on key parameter arguments

## Todos

  - Setup conda config and win bootstrap scripts.
  - Add template sub-package
  - packages for:
    - util : Logging, CLI, Config, etc.. just random non-central utility code
    - setup : Setup scripts for worker, server, celery, windows, etc..
    - adm.model : Intermediate rep that maps tightly to the adm format
  - dependency dir for submodules

## Other

  - Using python 3.9 since that's what a lot of things support

  - Config setup
    - Use `platformdirs` to get config dir and defaults for
