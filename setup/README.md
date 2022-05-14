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

## Subproject Organization (Needs updating)

```
<repo_root>
└──simpleuam-setup   # Subpackage Root Dir
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
   │   └── setup   # Root module for this package
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
