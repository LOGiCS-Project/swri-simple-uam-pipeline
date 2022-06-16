# General Machine Setup

This is setup that needs to be done for multiple types of machines.

### Prerequisites

- This machine must be running Windows.
    - If you're using a Linux machine skip to the setup page of whatever
      component type it's meant to host.
- You must be okay using [chocolatey](https://chocolatey.org/) as your package
  manager.

### Install Chocolatey and Minimal Deps

> This downloads a minimal install script for chocolatey, git, and python.
> This step is idempotent and will just do nothing if these are all installed.

- Open admin powershell and run:
  ```bash
  iwr -Uri https://raw.githubusercontent.com/LOGiCS-Project/swri-simple-uam-pipeline/main/data/setup/bootstrap_win.ps1 | iex
  ```

- Close this powershell terminal and open new ones for future steps.

### Download SimpleUAM

> Get this repo onto the machine somehow, cloning is the default method.
> If you have a shared drive, placing the repo there will allow local development
> without constant pushing and pulling.


- Save the repo's final location as `<repo-root>`.

#### **Option 1:** Clone from Github (HTTP):

```bash
git clone https://github.com/LOGiCS-Project/swri-simple-uam-pipeline.git <repo-root>
```

#### **Option 2:** Clone from Github (SSH):

```bash
git clone git@github.com:LOGiCS-Project/swri-simple-uam-pipeline.git <repo-root>
```

### Initialize Setup Package

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

### Get Configuration Directory

> The configuration directory holds `*.conf.yaml` files that determine how
> many aspects of a running SimpleUAM system operate.

- Navigate an admin powershell to `<repo_root>`.
- Print config directory:
  ```bash
  pdm run suam-config dir
  ```

- Save result as `<config-dir>`.

### Install Quality of Life Packages *(Optional)*

> This installs Firefox, Notepad++, Tess, and other applications that make working
> on a new windows install more bearable.

- Navigate an admin powershell to `<repo_root>`.
- Install the packages:
  ```bash
  pdm run setup-win install.qol-deps
  ```

### Setup File Sharing *(Optional)*

If you intend to share files (e.g. results) between workers and clients then
set that up now, if you haven't done so already.

If using AWS the instructions for the FSx file share take care of this.

Otherwise shared directory and file server configurations are too varied for us
to provide precise instructions.
The only real requirement is that worker nodes see the shared file storage as
a normal directory.

- Save the shared results directory as `<results-dir>`.

### Install an API token for `git.isis.vanderbilt.edu` *(Optional)*

> We can use an API token to automate some repository and file accesses using
> Isis that would otherwise require manual authentication.

#### Create a Personal Access Token

- Log into https://git.isis.vanderbilt.edu .
- Save your isis username as `<isis-user>`.
- Go to User Settings -> [Access Tokens](https://git.isis.vanderbilt.edu/-/profile/personal_access_tokens) .
    - **Token Name:** `<isis-token-name>`
    - **Expiration Date:** 2050-01-01
    - Select Scopes:
        - **`read_api`:** Check
        - **`read_repository`:** Check
        - All other others should be unchecked.
- Click "Create Personal Access Token".
- Save "Your new personal access token" as `<isis-token>`.

#### Configure SimpleUAM to use your token

- Open `<config-dir>/auth.conf.yaml` in a text editor.
- Set the `isis_user` field to `<isis-user>`
- Set the `isis_token` field to `<isis-token>`

??? example "Sample `auth.conf.yaml`"
    ```yaml
    isis_user: myIsisUsername
    isis_token: 'glpat-ASDsd79adAkslafo21GO'
    ```

### Install SSH keys for `git.isis.vanderbilt.edu` *(Optional)*

> SSH access to Isis, while not strictly necessary, will make future install
> steps easier and more secure.
> This doesn't do anything if an API token is already provided.

- Follow the instructions [here](https://docs.gitlab.com/ee/user/ssh.html) to
  set up ssh key based access to the isis server.

### Further Setup

Once this setup is complete you can continue to one or more of the following
steps.
All of the following nodes can coexist on a single windows instance.

**Continue to [Creo License Server Setup](license_server.md)...**<br/>
**Or to [Message Broker Setup](broker.md)...**<br/>
**Or to [Corpus DB Setup](graph.md)...**<br/>
**Or to [Static Corpus Setup](corpus.md)...**<br/>
**Or to [Worker Node Setup](worker.md)...**
