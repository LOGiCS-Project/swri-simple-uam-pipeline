# SimpleUAM Utility Modules

Various modules and wrappers for config, logging, and other general utilities.

**Note:** This entire file assumes you're already within this project's conda env.

## Setup

Run `invoke setup` while in `<repo_root>/util`.

## Installation

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
   ├── config   # Assorted Config Files
   │   │
   │   ├── flake8.ini     # Code Quality
   │   ├── mypy.ini       # Type Checking
   │   ├── coverage.ini   # Test Coverage
   │   └── pytest.ini     # Testing
   │
   ├── src
   │   └── util   # Root module for this package
   │       │
   │       ├── __init__.py   # Module Root
   │       ├── cli.py        # Entry Point for subpackage's CLI
   │       ├── __main__.py   # Stub wrapping cli.py (don't edit)
   │       └── py.typed      # Flag to indicate this module is typed
   │
   └── tests   # Testing Code
       │
       ├── __init__.py   # Module Root
       ├── conftest.py   # pytest configuration
       └── test_cli.py   # Minimal test of CLI functionality
```

## Development Tasks

### Dependency Management

See instructions on [the PDM website](https://pdm.fming.dev/usage/dependency/).

PDM will work as expected for most operations.

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