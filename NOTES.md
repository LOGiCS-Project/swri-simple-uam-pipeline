# Notes for future development

## Library Use

  - [platformdirs](https://pypi.org/project/platformdirs/) : For finding
    appropriate local config and working directories.
  - [pdm](https://pdm.fming.dev/) : Python build and dep management tool like
    poetry or pipenv. (Except it doesn't choke when a package author forgets
    a metadata field)
  - [invoke](https://docs.pyinvoke.org/en/stable/) : To act as a CLI interface
    wrapper for setup and evaluation.
  - [dynaconf](https://www.dynaconf.com/validation/) : for config management
    and parsing
  - [coloredlogs](https://pypi.org/project/coloredlogs/) : For pretty logs
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

## Other

  - Using python 3.9 since that's what a lot of things support
