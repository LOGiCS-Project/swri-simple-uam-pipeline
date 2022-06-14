# Static Corpus Setup

The graph database is far too bloated for practical use, instead we can
export the relevant information to a small json file and use that directly.

This file is needed for many of the tasks that worker nodes will do and needs
to be retrieved or generated.

## **Option 1:** Use static corpus provided in repo *(Recommended)*

This is the corpus for `all_schema_uam.graphml` generated in June '22.

### Prerequisites

- [General Setup](general.md) has been completed.

### Install Static Corpus

- Once configured open admin powershell at `<repo-root>`.
- Install the corpus provided with this repo:
  ```bash
  pdm run craidl static-corpus.copy
  ```

## **Option 2:** User a user provided static corpus

This will just load the user provided file into the install location.

### Prerequisites

- [General Setup](general.md) has been completed.
- The corpus we're installing is at `<static-corpus-loc>`.

### Install Static Corpus

- Once configured open admin powershell at `<repo-root>`.
- Install a user provided corpus from `<static-corpus-loc>`
  ```bash
  pdm run craidl static-corpus.copy --input=<static-corpus-loc>
  ```

## **Option 3:** Generate Static Corpus from a Corpus Database

This will generate a static corpus from a running graph server, using whatever
corpus it was configured with.

### Prerequisites

- [General Setup](general.md) has been completed.

### Configure Server Settings

> The config file at `<config-dir>/craidl.conf.yaml` stores information for
> connecting to a corpus DB server.

- Open admin powershell to `<repo-root>`.
- *(Optional)* View currently loaded config file:
  ```bash
  pdm run suam-config print --config=craidl -r
  ```
  The fields under `server_host` and `server_port` determine which corpus
  database this tool will connect to when generating a static corpus.
  The default options connect to a stub server running on the same machine.

- *(Optional)* If you're connecting to a corpus database not running on the
  current machine then update `<config-dir>/craidl.conf.yaml`.
    - Set `server_host` to `<corpus-db-ip>`.
    - Set `server_port` to `<corpus-db-port>`.

### Generate Static Corpus

- Ensure the server at `<corpus-db-ip>` is currently running.
- Generate the static corpus from that server.
  ```bash
  pdm run craidl static-corpus.generate
  ```

With default settings the corpus generation and the stub server can hang
intermittently, so the generation command periodically saves its progress.
Just rerun the command (with the same settings) and it will resume generating
the corpus from the last saved cluster of components.

**See the section on [using Craidl](../usage/Craidl) for information on
how to use the generated static corpus...**