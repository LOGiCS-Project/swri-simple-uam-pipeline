# General Machine Setup

This is setup that needs to be done for multiple types of machines.

## Prerequisites {#prereqs}

- This machine must be running Windows.
    - If you're using a Linux machine skip to the setup page of whatever
      component type it's meant to host.
- You must be okay using [chocolatey](https://chocolatey.org/) as your package
  manager.

## Install Chocolatey and Minimal Deps {#install-choco}

> This downloads a minimal install script for chocolatey, git, and python.
> This step is idempotent and will just do nothing if these are all installed.

- Open admin powershell and run:
  ```bash
  iwr -Uri https://raw.githubusercontent.com/LOGiCS-Project/swri-simple-uam-pipeline/main/data/setup/bootstrap_win.ps1 | iex
  ```

- Close this powershell terminal and open new ones for future steps.

## Download SimpleUAM {#suam}

> Get this repo onto the machine somehow, cloning is the default method.
> If you have a shared drive, placing the repo there will allow local development
> without constant pushing and pulling.

- Save the repo's final location as: `<repo-root>`

#### **Option 1**: Clone From Github (HTTP): {#suam-github-http}

- Clone from Github via HTTP, replacing `<repo-root>` in the following command:
  ```bash
  git clone https://github.com/LOGiCS-Project/swri-simple-uam-pipeline.git <repo-root>
  ```

#### **Option 2**: Clone From Github (SSH): {#suam-github-ssh}

- Clone from Github via SSH, replacing `<repo-root>` in the following command:
  ```bash
  git clone git@github.com:LOGiCS-Project/swri-simple-uam-pipeline.git <repo-root>
  ```

#### **Option 3**: Retrieve From Other Source {#suam-other}

Details are left to the user.

## Initialize Setup Package {#setup}

> Initialize pdm and packages for worker setup.

- Navigate an admin powershell to `<repo_root>`.
- Setup PDM environment for this repo:
  ```bash
  pdm install -d
  ```
- Test whether setup script was installed:
  ```bash
  pdm run setup-win --help
  ```
  Result should be a help message showing all of `setup-win`'s flags and
  subcommands.

## Get Configuration Directory {#conf-dir}

> The configuration directory holds `*.conf.yaml` files that determine how
> many aspects of a running SimpleUAM system operate.

- Navigate an admin powershell to `<repo_root>`.
- Print config directory:
  ```bash
  pdm run suam-config dir
  ```
- Save result as `<config-dir>`.

## Install Quality of Life Packages *(Optional)* {#qol}

> This installs Firefox, Notepad++, Tess, and other applications that make working
> on a new windows install more bearable.

- Navigate an admin powershell to `<repo_root>`.
- Install the packages:
  ```bash
  pdm run setup-win install.qol-deps
  ```
- Close this powershell terminal and open new ones for future steps.

!!! Info ""
    One of the default QoL packages, [Tess](https://tessapp.dev/), is
    significantly nicer to use than the native powershell terminal.
    Consider using it to create an admin powershell instead of the OS-provided
    terminal.

## Setup File Sharing *(Optional)* {#nfs}

If you intend to share files (e.g. results) between workers and clients then
set that up now, if you haven't done so already.

If using AWS the instructions for the FSx file share take care of this.

Otherwise shared directory and file server configurations are too varied for us
to provide precise instructions.
The only real requirement is that worker nodes see the shared file storage as
a normal directory.

- Save the shared results directory as `<results-dir>`.

## Set up Isis Authentication {#isis}

> Various private resources are on git.isis.vanderbilt.edu.
> So that they aren't made available to the public SimpleUAM will retrieve any
> non-public information using credentials you provide.

### **Option 1**: Install an API token for `git.isis.vanderbilt.edu` *(Recommended)* {#isis-token}

> We can use an API token to automate some repository and file accesses using
> Isis that would otherwise require manual authentication.

#### Create a Personal Access Token {#isis-token-create}

- Log into https://git.isis.vanderbilt.edu .
- Save your isis username as: `<isis-auth.user>`
- Go to "User Settings" -> "[Access Tokens](https://git.isis.vanderbilt.edu/-/profile/personal_access_tokens)".
    - **Token Name**: `<isis-auth.token-name>`
    - **Expiration Date**: 2100-01-01
    - Select Scopes:
        - **`read_api`**: Check
        - **`read_repository`**: Check
        - All other others should be unchecked.
- Click "Create Personal Access Token".
- Save "Your new personal access token" as: `<isis-auth.token>`

#### Configure SimpleUAM to use your token {#isis-token-config}

- Open `<config-dir>/auth.conf.yaml` in a text editor.
    - Set the `isis_user` field to `<isis-auth.user>`
    - Set the `isis_token` field to `<isis-auth.token>`

    ??? example "Sample `auth.conf.yaml`"
        ```yaml
        --8<-- "docs/assets/config/auth.conf.yaml"
        ```

### **Option 2**: Install SSH keys for `git.isis.vanderbilt.edu` {#isis-ssh}

> SSH access to Isis, while not strictly necessary, will make future install
> steps easier and more secure.
> This doesn't do anything if an API token is already provided.

- Follow the instructions [here](https://docs.gitlab.com/ee/user/ssh.html) to
  set up ssh key based access to the isis server.

### **Option 3**: Skip Authentication {#isis-skip}

> If you skip authentication here you will prompted for passwords when
> cloning repositories and asked to manually download files when needed.

## Next Steps {#next}

Once this setup is complete you can continue to one or more of the following
steps.
All of the following nodes can coexist on a single windows instance.

**Continue to [Creo License Server Setup](license_server.md)...**<br/>
**Or to [Message Broker Setup](broker.md)...**<br/>
**Or to [Corpus DB Setup](graph.md)...**<br/>
**Or to [Static Corpus Setup](corpus.md)...**<br/>
**Or to [Worker Node Setup](worker.md)...**
