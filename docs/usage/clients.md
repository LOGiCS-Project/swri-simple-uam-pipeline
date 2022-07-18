# SimpleUAM Client Nodes

Client nodes create designs in the SRI format and send those designs to a
SimpleUAM deployment to be processed.

## Configuration Instructions {#config}

See [here](../../setup/client/#broker) for instructions on how to set up a client
node.

!!! todo "TODO: Details"

## Client Tasks via CLI {#CLI}

See [here](../../setup/client#test) for basic interface.

There are two available sub-commands:

- **`direct2cad.gen-info-files`**: Generates info files for a given design.
- **`direct2cad.process-design`**: Runs Creo and FDM for a given design.

Which can be run using the `suam-client` entry point, shown with the mandatory
arguments for the input design (`<design-file>`) and the results directory
(`<results-dir>`):

```bash
pdm run suam-client <sub-command> --design=<design-file> --results=<results-dir>
```

This print some logs to stderr and the location of newly created results archive
to stdout.

**Arguments:**

- **`-d <design-file>`/`--design=<design-file>`**: *(Mandatory)*
  The design file, usually `design_swri.json`, to use as an input to the command.
- **`-r <results-dir>`/`--results=<results-dir>`**: *(Mandatory)*
  The results directory, as accessible to the client, where the result archives
  will appear on completion.
- **`-m <metadata-file>`/`--metadata=<metdata-file>`**:
  An optional file with JSON-encoded metadata that will be included with the
  `metadata.json` in the result archive.
  The metadata must be a JSON dictionary so that fields like `message_info`,
  `session_info`, and `result_archive` can be added.
- **`-b`/`--backend`**: Force the use of a dramatiq backend to detect when a
  sub-command has been finished by a worker.
  Will fail if no suitable backend is enabled.
- **`-p`/`--polling`**: For the use of polling to find completed results.
  This watches the results directory looking for an archive with the appropriate
  message id.
  This method is the default when no backend is available.
- **`-t <int>`/`--timeout=<int>`**: How long to wait, in seconds, before giving
  up on the command.
- **`-i <int>/`--interval=<int>`**: The interval between checks for a new result.
  Will check using the backend if used, otherwise will scan the results directory
  for new zip files.

Use the following for additional help:

```bash
pdm run suam-client <sub-command> --help
```

## Client Tasks via Python Interface {#python}

Look at the example project [here](https://github.com/LOGiCS-Project/swri-simple-uam-example).

!!! todo "TODO: Details"

### Basic Tasks {#python-tasks}

!!! todo "TODO: Details"

### Custom Metadata {#python-metadata}

!!! todo "TODO: Details"

### Waiting for results with Backends and Polling {#python-watch}

Results will appear as zip files in a results directory and there are
two ways for a client application to find them.

- **Backend**: If a backend is configured a function can be used to see if
  the sent task has been completed.
- **Polling**: The process can watch the results dir for new files and check
  their metadata to see if they correspond with the sent message.

See the [example client](#example) for more details.

!!! todo "TODO: Details"

### Example Client {#python-example}

Find an example project at [this github repo](https://github.com/LOGiCS-Project/swri-simple-uam-example).

!!! todo "TODO: More thorough break down"
