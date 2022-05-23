# SimpleUAM Workspace Setup

Instructions for setting up a worker machine so that it can run the commands
from this package.

## General Worker Setup

Make sure you've completed the worker setup instructions from the [`setup`
subpackage](../setup/README.md).

  - Follow the instructions [here](../setup/README_WORKER.md) if you haven't
    already.
  - If you use another setup method make sure that you have the following
    before continuing:
    - A working conda environment based on `<repo-root>/environment.yml`.
    - `git` and `rync` installed.
    - Creo 5.6 installed with the appropriate licenses config edits.
      - `pdm run setup install.creo` will apply the config edits automatically
        if creo is already installed.
    - This repo located at `<repo-root>`.
    - TODO: Probably some other things that the scripts install too.

## Python Environment Setup

Setup the python environment with pdm.

  - Open an admin powershell with the 'simple-uam' conda environment
    to `<repo-root>/util`.
  - Run: `invoke setup`

  - Open an admin powershell with the 'simple-uam' conda environment
    to `<repo-root>/uam-workspace`.
  - Run: `invoke setup`

## Initialize Git Submodules

Initialize and update the git submodules

  - Install an ssh key for `git.isis.vanderbilt.edu` or have your username and
    password handy.
  - Open an admin powershell with the 'simple-uam' conda environment
    to `<repo-root>/uam-workspace`.
  - Run: `pdm rum uam-workspace reference.init-swri-repos`
  - If no SSH key was installed fill username and password when prompted.
