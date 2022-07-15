# Static Corpus Setup

The graph database is far too bloated for practical use, instead we can
export the relevant information to a small json file and use that directly.

This file is needed for many of the tasks that worker nodes will do and needs
to be retrieved or generated.

## **Option 1:** Use static corpus provided in repo *(Recommended)* {#repo}

> This static corpus was generated from `all_schema.graphml` on July 15th '22.

### Prerequisites {#repo-prereqs}

- [General Setup](general.md) has been completed.

### Install Static Corpus {#repo-install}

- Once configured open admin powershell at `<repo-root>`.
- Install the corpus provided with this repo:
  ```bash
  pdm run craidl static-corpus.copy
  ```

## **Option 2:** User a user provided static corpus {#copy}

This will just load the user provided file into the install location.

### Prerequisites {#copy-prereqs}

- [General Setup](general.md) has been completed.
- The corpus to be installed at `<static-corpus-loc>`.

### Install Static Corpus {#copy-install}

- Once configured open admin powershell at `<repo-root>`.
- Install a user provided corpus from `<static-corpus-loc>`
  ```bash
  pdm run craidl static-corpus.copy --input=<static-corpus-loc>
  ```

## **Option 3:** Generate Static Corpus from a Corpus Database {#generate}

This will generate a static corpus from a running graph server, using whatever
corpus it was configured with.

### Prerequisites {#generate-prereqs}

- [General Setup](general.md) has been completed.

### Configure Server Settings {#generate-configure}

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
  current machine then create or update `<config-dir>/craidl.conf.yaml`.
    - Set `server_host` to `<corpus-db.ip>`.
    - Set `server_port` to `<corpus-db.port>`.

### Generate Static Corpus {#generate-run}

- Ensure the server at `<corpus-db.ip>` is currently running.
- Generate the static corpus from that server.
  ```bash
  pdm run craidl static-corpus.generate
  ```

!!! note ""
    The stub server seems to hang when out of memory or CPU, halting the
    serialization process.

    To mitigate this the generation process periodically saves the serialized
    component data and skips re-downloading saved data.
    By default every cluster of 50 components is saved to disk.

    Just rerun the command (with the same settings) and it will resume generating
    the corpus from the last saved cluster of components.


**See the section on [using Craidl](../usage/Craidl) for information on
how to use the generated static corpus...**
