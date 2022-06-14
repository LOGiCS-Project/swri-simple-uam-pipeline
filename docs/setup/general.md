# General Machine Setup

This is setup that needs to be done for multiple types of machines.

### Prerequisites

- This machine must be running Windows.
    - If you're using a Linux machine skip to the setup page of whatever
      component type it's meant to host.
- You must be okay using [chocolatey](https://chocolatey.org/) as your package
  manager.

### Install Chocolatey and Minimal Deps

This downloads a minimal install script for chocolatey, git, and python.
This step is idempotent and will just do nothing if these are all installed.

- Open admin powershell and run:
    - `iwr -Uri https://raw.githubusercontent.com/LOGiCS-Project/swri-simple-uam-pipeline/main/data/setup/bootstrap_win.ps1 | iex`
- Close this powershell terminal and open new ones for future steps.

### Download SimpleUAM

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
- Setup PDM environment for this repo:
    - Run: `pdm install -d`
- Test whether setup script was installed:
    - Run: `pdm run setup-win --help`

### Install Quality of Life Packages *(Optional)*

This installs Firefox, Notepad++, Tess, and other applications that make working
on a new windows install more bearable.

- Navigate an admin powershell to `<repo_root>`
    - Run: `pdm run setup-win install.qol-deps`

### Setup File Sharing *(Optional)*

If you intend to share files (e.g. results) between workers and clients then
set that up now, if you haven't done so already.

### Further Setup

Once this setup is complete you can continue to one or more of the following
steps.
All of the following nodes can coexist on a single windows instance.

**Continue to [Creo License Server Setup](license_server.md)...**<br/>
**Or to [Message Broker Setup](broker.md)...**<br/>
**Or to [Engineering Corpus Setup](corpus.md)...**<br/>
**Or to [Worker Node Setup](worker.md)...**
