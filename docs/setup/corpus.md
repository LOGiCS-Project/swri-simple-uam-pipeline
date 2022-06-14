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
- Install the corpus provided with this repo.
    - Run: `pdm run craidl static-corpus.copy`

## **Option 2:** User a user provided static corpus

This will just load the user provided file into the install location.

### Prerequisites

- [General Setup](general.md) has been completed.
- The corpus to install at `<static-corpus-loc>`

### Install Static Corpus

- Once configured open admin powershell at `<repo-root>`.
- Install a user provided corpus from `<static-corpus-loc>`
    - Run: `pdm run craidl static-corpus.copy --input=<static-corpus-loc>`

## **Option 3:** Generate from corpus database

This will generate a static corpus from a running graph server, using whatever
corpus it was configured with.

### Prerequisites

- [General Setup](general.md) has been completed.
- A running corpus DB at `<corpus-db-ip>` on port `<corpus-db-port>`

### Configure Server Settings

- Make sure a graph server is running at the configured location.
    - Examine loaded config with `pdm run suam-config print --config=craidl -r`
    - Server should be running at `server_host` on port `server_port`
    - Defaults would use a local stub server.

### Generate Static Corpus

- Generate the static corpus from that server.
    - Run: `pdm run craidl static-corpus.generate`

With default settings the corpus generation and the stub server can hang
intermittently, so the generation command periodically saves its progress.
Just rerun the command (with the same settings) and it will resume generating
the corpus from the last saved cluster of components.
