# swri-simple-uam-pipeline

Wrappers and installers for the SWRI UAM analysis pipeline that cut out
unnecessary cruft.

## Basic Setup

Install a conda environment and use `conda env create -f environment.yml` to
initialize the environment for these repos.

If you're setting up a windows worker node or license server then more
detailed instructions are linked from [here](setup/README.md).

## Development Commands

Update the conda environment when environment.yml is changed:

  - Run `invoke update-conda` in this directory while in the `simple-uam`
    conda environment.

Create a new subproject from the template:

  - Run `invoke new-subpackage` while in the conda environment.
  - The newly created files have comments and examples.
    - `<subpkg-dir>/README.md`: General setup and use information.
    - `<subpkg-dir>/src/<subpkg-module>/cli.py`: Has examples for key features
      like logging, CLI development, and config management.
