# Graph Server Setup

SWRi distributes their corpus of design data as a graph database that needs to
be queried for various tasks.

SimpleUAM provides utilities for running a *non-persistent* server for this
data using [TinkerPop](https://tinkerpop.apache.org)'s reference implementation.
This implementation isn't meant to be performant and should only be used to
temporarily serialize the corpus into a sensible format.

Ensure you've completed the steps in [General Setup](general.md) already.

### Install Dependencies

Install utilities like wget and rsync.

- Open an admin powershell to `<repo-root>`:
    - Run: `pdm run setup-win install.graph-deps`
- Reboot the machine.

**Instructions on configuration and use are [here](../usage/craidl.md)...**
