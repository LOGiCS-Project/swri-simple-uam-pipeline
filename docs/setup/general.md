# General Node Setup

This is setup that needs to be done for multiple types of nodes.

  - Windows only
  - uses choco (mandatory!)
  - setup env

### Install Chocolatey and Minimal Deps

This downloads a minimal install script for chocolatey, git, and python.
This step is idempotent and will just do nothing if these are all installed.

  - Open admin powershell and run:
    - `iwr -Uri https://raw.githubusercontent.com/LOGiCS-Project/swri-simple-uam-pipeline/main/data/setup/bootstrap_win.ps1 | iex`
  - Close this powershell terminal and open new ones for future steps.

### Get This Repo

Get this repo onto the machine somehow, cloning is the default method.
If you have a shared drive, placing the repo there will allow local development
without constant pushing and pulling.

  - **Option 1:** Clone from Github (HTTP):
    - `git clone https://github.com/LOGiCS-Project/swri-simple-uam-pipeline.git`
  - **Option 2:** Clone from Github (SSH):
    - `git clone git@github.com:LOGiCS-Project/swri-simple-uam-pipeline.git`

From here `<repo-root>` will refer to the repo's location.

### Initialize Setup Package

Initialize pdm and packages for worker setup.

  - Navigate an admin powershell to `<repo_root>`
  - Setup sub-package pdm environment:
    - Run: `pdm install -d`
  - Test whether setup script was installed:
    - Run: `pdm run setup-win --help`

### *(Optional)* Install Quality of Life Packages

This installs Firefox, Notepad++, Tess, and other applications that make working
on a new windows install more bearable.

  - Navigate an admin powershell to `<repo_root>`
    - Run: `pdm run setup-win install.qol-deps`

### Further Setup

Once this setup is complete you can continue to one or more of the following
steps.
All of the following nodes can coexist on a single windows instance.

**Continue to [Creo License Server Setup](license_server.md)...**<br/>
**Or to [Message Broker Setup](broker.md)...**<br/>
**Or to [Graph Server Setup](graph.md)...**<br/>
**Or to [Worker Node Setup](worker.md)...**
