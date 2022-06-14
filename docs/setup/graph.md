# Corpus Database Setup

SWRi distributes their corpus of design data as a graph database that needs to
be queried for various tasks.

## **Option 1:** Running a Local Stub Server *(Recommended)*

This is a local, minimal version of a corpus DB that uses
[TinkerPop](https://tinkerpop.apache.org)'s reference graph db implementation.
It is not persistent so no changes will be preserved between restarts.

### Prerequisites

- [General Setup](general.md) has been completed.
- If not using the default corpus have the `.graphml` corpus ready at
  `<corpus-loc>`.
- If using default corpus have SSH keys or credentials for
  `git.isis.vanderbilt.edu`.

### Install Dependencies

Install utilities like wget and rsync.

- Open an admin powershell to `<repo-root>`:
    - Run: `pdm run setup-win install.graph-deps`
- Reboot the machine.

### Install GraphML Corpus

**Option 1**: Download default from athens-uav-workflows

- In admin powershell at `<repo-root>`.
- Download athens-uav-workflows repo and get `all_schema_uam.graphml`
    - Run: `pdm run craidl corpus.download`
    - Follow prompts, enter git.isis.vanderbilt.edu credentials if needed.
- Install corpus to default location.
    - Run: `pdm run craidl corpus.install`
    - Default parameters will use downloaded corpus.

**Option 2**: Install from provided file

- In admin powershell at `<repo-root>`.
- Install user provided corpus from `<corpus-loc>`.
    - Run: `pdm run craidl corpus.install --corpus=<corpus-loc>`

### Configure Corpus Server

- In admin powershell at `<repo-root>`.
- Craidl settings file:
    - Examine loaded config with `pdm run suam-config print --config=craidl -r`
    - Server will use `stub_server.host` and `stub_server.port` by default.
    - Change `stub_server.host` to `0.0.0.0` if you aren't just using this
      DB locally.
- Install and configure corpus DB
    - Run: `pdm run craidl stub-server.configure`
    - Will use configured host, port, and graphml corpus.

### Open Required Ports

!!! Note
    If you only intend to use the stub database with local workers and clients.
    then you don't need to open ports up.

Open the relevant ports up so workers can connect:

- Open up port `<corpus-db-port>` (default: 8182).
    - Instructions will likely be setup specific.
- **(Optional)** If on Windows Server 2019 you can disable the firewall completely.

    !!! warning
        This is not secure at all. Do not do this if the license
        server is at all accessible from public or untrusted computers.

        Run: `pdm run setup-win license-server.disable-firewall`

### Run Corpus Server

- Once configured open admin powershell at `<repo-root>`.
- Run the graph server as a process.
    - Run: `pdm run craidl stub-server.run`
    - Note that this isn't a service, the server will stop if you close the
      terminal.

### Preserve Settings

If you're connecting from a different machine.

- Keep this machine's IP as: `<corpus-db-ip>`
- Keep the database's open port as: `<corpus-db-port>` (default: 8182)

## **Option 2:** Run a full corpus database.

We try to avoid using the SWRi provided graph database and haven't explored
alternate options, so this is up to you.

### Preserve Settings

If you're connecting from a different machine.

- Keep this machine's IP as: `<corpus-db-ip>`
- Keep the database's open port as: `<corpus-db-port>` (default: 8182)
