# SimpleUAM Setup Scripts

Performs various setup tasks for workers and server nodes.

Instructions for each type of server are in the corresponding README_*.md files
in this directory.

  - [AWS Instructions](README_AWS.md): Do this first if you're using AWS to
    host the various servers.
  - [License Server](README_LICENSE.md): Instructions for setting up a CREO
    license server. (Still in old form, needs updating)
  - [Worker Server](README_WORKER.md): Instructions for setting up a worker
    node, at least the basic prerequisites.
    Instructions specific to a particular sub-package will be in that
    sub-package.

**Note:** This entire file assumes you're already within this project's conda env.

## Usage

By default SimpleUAM Setup Scripts can be used as a standard python library or
with a command line interface.

### As a Command Line Interface

Run the command defined in `setup.cli:main` as follows:

```bash
pdm run setup <args>
```

Global help information uses the `-h`/`--help` flag and, among other things, lists
all available subcommands:

```bash
pdm run setup --help
```

Individual subcommands have their own help pages (taken from docstrings):

```bash
pdm run setup <sub-command> --help
```

### As a Library

See instructions on [the PDM website](https://pdm.fming.dev/usage/dependency/).

PDM will work as expected for most operations.

Adding relative imports requires adding the following line
to the dependencies field of `pyproject.toml`:

```toml
    "-e ./../<path_from_repo_root>",
```

Where `<path_from_repo_root>` is the path from the repo root, to the folder
containing the dependency's `pyproject.toml`, `setup.py`, or similar config.

From there you should be able to import modules as normal, e.g.:

```python
import setup
```

## Subproject Organization (Needs updating)

```
<repo_root>
└──setup   # Subpackage Root Dir
   │
   ├── README.md        # This README file
   ├── pyproject.toml   # PDM managed project info
   ├── tasks.py         # Commands for project management, called with `invoke`
   │
   ├── src
   │   └── setup   # Root module for this package
   │       │
   │       ├── config   # Configuration files and defaults
   │       │   │
   │       │   ├── __init__.py.jinja              # Module Root
   │       │   └── worker_setup_config.py.jinja   # Install Pkg Lists
   │       │
   │       ├── tasks   # CLI setup tasks
   │       │   │
   │       │   ├── shared.py           # Tasks for all systems
   │       │   ├── license_server.py   # Tasks for license server setup
   │       │   └── worker.py           # Tasks for worker setup
   │       │
   │       ├── windows   # Windows specific setup helpers
   │       │   │
   │       │   ├── __init__.py   # Module Root
   │       │   ├── helpers.py    # General windows helpers incl. GUI installers
   │       │   └── choco.py      # Tasks for working with Chocolatey
   │       │
   │       ├── __init__.py   # Module Root
   │       ├── __main__.py   # Stub wrapping cli.py (don't edit)
   │       ├── cli.py        # Entry Point for subpackage's CLI
   │       └── py.typed      # Flag to indicate this module is typed
   │
   └── tests   # Testing Code
       │
       ├── __init__.py   # Module Root
       ├── conftest.py   # pytest configuration
       └── test_cli.py   # Minimal test of CLI functionality
```

## Development Tasks

Assorted tasks used during development, mostly automated with the `invoke` command
(as opposed to runtime tasks which use `pdm run setup`).

### Dependency Management

See instructions on [the PDM website](https://pdm.fming.dev/usage/dependency/).

PDM will work as expected for most operations, with the exception of relative
imports of other packages in this repo.

Adding relative imports requires adding the following line
to the dependencies field of `pyproject.toml`:

```toml
    "-e ./../<path_from_repo_root>",
```

Where `<path_from_repo_root>` is the path from the repo root, to the folder
containing the dependency's `pyproject.toml`, `setup.py`, or similar config.

### Running Tests

Run the full suite with: `invoke test`

Run a subset of tests with: `invoke test --match="<filter_string>"`

Generate a code coverage report with: `invoke coverage`

### Code Quality

Run type checking: `invoke check-types`

Run code linter: `invoke check-quality`

Run both of the above: `invoke check`

Run code formatter: `invoke format`

## Other

Clean temporary dev files: `invoke clean`
