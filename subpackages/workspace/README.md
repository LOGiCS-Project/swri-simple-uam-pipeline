# SimpleUAM Workspace

Manages various actions to manipulate designs and run them through cad generation, FDM, and other processes. Also handles creating worker nodes for server interactions.

**Setup instructions are [here](SETUP.md).**

**Note:** This entire file assumes you're already within this project's conda env.

## Usage

By default SimpleUAM Workspace can be used as a standard python library or
with a command line interface.

### Initialize PDM

Initialize the package by running `invoke setup` in this directory, once finished
`pdm run` becomes available for use.

Running `invoke reset-pdm` will delete the entire PDM environment letting you
run `invoke setup` again.

### As a Command Line Interface

Run the command defined in `uam_workspace.cli:main` as follows:

```bash
pdm run uam-workspace <args>
```

Global help information uses the `-h`/`--help` flag and, among other things, lists
all available subcommands:

```bash
pdm run uam-workspace --help
```

Individual subcommands have their own help pages (taken from docstrings):

```bash
pdm run uam-workspace <sub-command> --help
```

### As a Library

To use this package as a dependency in other subpackages add the following line
to the dependencies field of `pyproject.toml`:

```toml
    "-e ./../uam-workspace",
```

Other relative dependencies need to be added in the same way, by direcctly adding
the path (prefixed with `./`) to the `pyproject.toml`.

Then run `invoke setup` or, equivalently, `pdm install`.

From there you should be able to import modules as normal, e.g.:

```python
import uam_workspace
```

## Subproject Organization

```
<repo_root>
└──uam-workspace   # Subpackage Root Dir
   │
   ├── README.md        # This README file
   ├── pyproject.toml   # PDM managed project info
   ├── tasks.py         # Commands for project management, called with `invoke`
   │
   ├── src   # Root of Module Hierarchy
   │   │
   │   └── uam_workspace   # Root module for this package
   │       │
   │       ├── config   # Configuration files and defaults
   │       │   │
   │       │   ├── __init__.py.jinja    # Module Root
   │       │   └── dataclass.py.jinja   # Dataclass w/ config file info.
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
(as opposed to runtime tasks which use `pdm run uam-workspace`).

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

Reset PDM environment: `invoke reset-pdm`