# Corpus Database Setup

SWRi distributes their corpus of design data as a graph database that needs to
be queried for various tasks.

## **Option 1:** Running a Local Stub Server *(Recommended)* {#stub}

> This is a local, minimal version of a corpus DB that uses
> [TinkerPop](https://tinkerpop.apache.org)'s reference graph db implementation.
> It is not persistent so no changes will be preserved between restarts.

### Prerequisites {#stub-prereqs}

- [General Setup](general.md) has been completed.
- If not using the default corpus have the `.graphml` corpus ready at
  `<corpus-loc>`.
- If using the default corpus have an auth token, SSH keys, or credentials for
  `git.isis.vanderbilt.edu` set up.

### Install Dependencies {#stub-deps}

> Install utilities like wget and rsync.

- Open an admin powershell to `<repo-root>`.
- Install dependencies:
  ```bash
  pdm run setup-win install.graph-deps
  ```
- Reboot the machine.

### Install GraphML Corpus {#stub-corpus}

> We need to install the GraphML corpus to a default location so future setup
> steps can find it.

#### **Option 1**: Download default from athens-uav-workflows {#stub-corpus-download}

- Open an admin powershell at `<repo-root>`.
- Automatically download athens-uav-workflows repo and get
  `all_schema_uam.graphml`:
  ```bash
  pdm run craidl corpus.download
  ```

- Follow prompts, entering in `git.isis.vanderbilt.edu` credentials if needed.
- Install corpus to default location:
  ```bash
  pdm run craidl corpus.install
  ```

#### **Option 2**: Install corpus from user provided file {#stub-corpus-file}

- Open admin powershell to `<repo-root>`.
- Install user provided corpus from `<corpus-loc>`:
  ```bash
  pdm run craidl corpus.install --corpus=<corpus-loc>
  ```

### Configure Corpus DB Server {#stub-configure}

> The config file at `<config-dir>/craidl.conf.yaml` stores information for
> running SimpleUAM's stub corpus database.
> Those settings are then used to configure the stub server.

- Open admin powershell to `<repo-root>`.
- *(Optional)* View currently loaded configuration:
  ```bash
  pdm run suam-config print --config=craidl -r
  ```
  The fields under `stub_server.host` and `stub_server.port` determine how the
  corpus is served.

- *(Optional)* If serving the graph to other machines then update or create the
  `stub_server.host` config property.
    - Set `stub_server.host` to `0.0.0.0`.
    - See the [config file guide](../usage/config.md) for more detailed
      instructions and information.

- Install and configure corpus DB:
  ```bash
  pdm run craidl stub-server.configure
  ```
  In the absence of any arguments this uses the configured host, port, and
  graphml corpus from `<corpus-dir>/craid.conf.yaml`.

### Run Corpus DB Server *(Optional)* {#stub-run}

> This runs the corpus DB stub server as a local process.
> Use it as needed, especially when generating a static corpus.

- Run corpus DB:
  ```bash
  pdm run craidl stub-server.run
  ```
- Kill the process manually (usually with Ctrl-C) when finished.

### Open Required Ports *(Optional)*

> Open the relevant ports up so that non-local worker nodes can
> connect to the stub database.
>
> We do not recommend non-local connections to a stub corpus database.

!!! Note ""
    If you only intend to connect to a local worker node or locally
    generate a static corpus then you don't need to open any ports up.

#### **Option 1:** Open only port 8182.

The instructions for this are too configuration specific for us to provide.

#### **Option 2:** Disable corpus DB firewalls entirely.

We can't provide general instructions for this step but if you're using
Windows Server 2019 you can use one of our scripts.

!!! warning "Do not do this on public or untrusted machines"

- Disable the Windows Server 2019 firewall:
  ```bash
  pdm run setup-win disable-firewall
  ```

**Note:** This might work with other versions of Windows but that hasn't been
tested.

### Preserve Settings

> If you're connecting from a different machine.

- Keep this machine's IP as: `<corpus-db.ip>`
- Keep the database's open port as: `<corpus-db.port>` (default: 8182)


## **Option 2:** Run a full corpus database.

We try to avoid using the SWRi provided graph database and haven't explored
alternate options, so this is up to you.

### Preserve Settings

> If you're connecting from a different machine.

- Keep this machine's IP as: `<corpus-db.ip>`
- Keep the database's open port as: `<corpus-db.port>` (default: 8182)

## Next Steps

**Generate a static corpus with the instructions [here](../corpus)...**<br/>
**See the section on [using Craidl](../usage/craidl) for information on
how to run and use this server...**
