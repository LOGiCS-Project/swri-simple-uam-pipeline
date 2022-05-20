# SimpleUAM Utility Modules

Various modules and wrappers for config, logging, and other general utilities.

**Note:** This entire file assumes you're already within this project's conda env.

## Usage

By default SimpleUAM can be used as a standard python library or
with a command line interface.

### As a Command Line Interface

Run the command defined in `util.cli:main` as follows:

```bash
pdm run simpleuam-utils <args>
```

Global help information uses the `-h`/`--help` flag and, among other things, lists
all available subcommands:

```bash
pdm run simpleuam-utils --help
```

Individual subcommands have their own help pages (taken from docstrings):

```bash
pdm run simpleuam-utils <sub-command> --help
```

### As a Library

To use this package as a dependency in other subpackages add the following line
to the dependencies field of `pyproject.toml`:

```toml
    "-e ./../util",
```

Other relative dependencies need to be added in the same way, by direcctly adding
the path (prefixed with `./`) to the `pyproject.toml`.

Then run `invoke setup` or, equivalently, `pdm install`.

From there you should be able to import modules as normal, e.g.:

```python
import util
```

## Setup

Run `invoke setup` while in `<repo_root>/util`.

## Installation


## Usage

Run the command defined in `util.cli:main` as follows:

```bash
pdm run simpleuam-utils <args>
```

## Subproject Organization

```
<repo_root>
└──util   # Subpackage Root Dir
   │
   ├── README.md        # This README file
   ├── pyproject.toml   # PDM managed project info
   ├── tasks.py         # Commands for project management, called with `invoke`
   │
   ├── src
   │   └── util   # Root module for this package
   │       │
   │       ├── config   # Handles all project configuration files and settings.
   │       │   │
   │       │   ├── __init__.py      # Module Root
   │       │   ├── manager.py       # Exports `Config` manager class
   │       │   ├── path_config.py   # Config for important environment paths
   │       │   └── tasks.py         # Tasks used in CLI for managing configs
   │       │
   │       ├── invoke   # Wrapper for default CLI library.
   │       │   │
   │       │   ├── __init__.py   # Module Root
   │       │   └── program.py    # Wrapper CLI class
   │       │
   │       ├── logging  # Wrapper for logging
   │       │   │
   │       │   ├── __init__.py   # Module Root
   │       │   └── logger.py     # Wraps `structlog`'s logger function.
   │       │
   │       ├── paths  # Important Environment Paths
   │       │   │
   │       │   ├── __init__.py   # Module Root
   │       │   └── app_dirs.py   # Handles for important application directories
   │       │
   │       ├── system   # Helpers for system operations
   │       │   │
   │       │   ├── __init__.py   # Module Root
   │       │   ├── backup.py     # Routines to create backup files
   │       │   └── windows.py    # Windows specific routines
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
(as opposed to runtime tasks which use `pdm run simpleuam-utils`).

### Dependency Management

See instructions on [the PDM website](https://pdm.fming.dev/usage/dependency/).

This package shouldn't import any other subpackages in this repo.

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
