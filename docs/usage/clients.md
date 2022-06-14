# SimpleUAM Client Nodes

- Client sends out requests to message broker for analysis
    - Watches shared file directory for results.
    - If backend set up then maybe gets notified.
    - Must be connected to same broker as the worker nodes.
- Two sessions:
    - `gen_info_files` : Same as craidl and workspace versions, except ships
      out to worker for evaluation.

        !!! example "Command Line:"

            ```bash
            pdm run d2c-client gen-info-files -i design_swri.json
            ```

        !!! example "Python:"
            ```python
            from simple_uam import direct2cad
            msg = direct2cad.gen_info_files.send(design)
            ```

    - `process design`: same ad d2c workspace version except ships out to worker
      for eval.

        !!! example "Command Line:"

            ```bash
            pdm run d2c-client process-design -i design_swri.json
            ```

        !!! example "Python:"
            ```python
            from simple_uam import direct2cad
            msg = direct2cad.process_design.send(design)
            ```

- Talk about config file `d2c_worker.conf.yaml` and fields:
    - Broker config
    - Backend config

??? todo "reqs"
    - Clients:
        - Config broker and backend
        - Run pipeline vie CLI
        - Run pipeline via python

### Making a Client Request via Command Line

A client needs to have a broker configured in its `<config-dir>/d2c_worker.conf.yaml`
just like the worker node.

By default it can only send requests to workers and it won't receive any
response back. If both the worker and client have an enabled and configured
backend then the client will receive metadata which includes the name of the
archive file generated in response to the original request.

The client doesn't need any of the other setup of a worker node past having
this repo available and the proper configuration.
All of this works on Linux and OS X, not just Windows.

Send a `gen_info_files` request using the command line interface:

```bash
PS D:\simple-uam> pdm run d2c-worker gen-info-files --help
Usage: pdm run d2c-worker [--core-opts] gen-info-files [--options] [other tasks here ...]

Docstring:
  Will write the design info files in the specified
  workspace, and create a new result archive with only the newly written data.
  The workspace will be reset on the next run.

  Arguments:
    input: The design file to read in.
    metadata: The json-format metadata file to include with the query.
      Should be a dictionary.
    output: File to write output session metadata to, prints to stdout if
      not specified.

Options:
  -i STRING, --input=STRING
  -m STRING, --metadata=STRING
  -o STRING, --output=STRING
```

Send a `process_design` request using the command line interface:

```bash
PS D:\simple-uam> pdm run d2c-worker process-design --help
Usage: pdm run d2c-worker [--core-opts] process-design [--options] [other tasks here ...]

Docstring:
  Runs the direct2cad pipeline on the input design files, producing output
  metadata and a records archive with all the generated files.

  Arguments:
    input: The design file to read in.
    metadata: The json-format metadata file to include with the query.
      Should be a dictionary.
    output: File to write output session metadata to, prints to stdout if
      not specified.

Options:
  -i STRING, --input=STRING
  -m STRING, --metadata=STRING
  -o STRING, --output=STRING
```

### Making a Client Request in Python

The configuration requirements are identical to the command-line case.

Sending a request requires:

  - SimpleUAM and `dramatiq` as dependencies.
  - `design` as a JSON-serializable python object.
  - Optional `metadata` a JSON-serializable python dictionary.

A basic example:

```python
from simple_uam import direct2cad
from simple_uam.util.config import Config, D2CWorkerConfig

design = your_code_here()
metadata = your_code_here()

msg = direct2cad.process_design.send(design, metadata=metadata)

# Only works if we have a configured and enabled backend to cache results.
if Config[D2CWorkerConfig].backend.enabled:
    result = msg.get_result(block=True,timeout=600000)
    print(result)
```

The core task processing is handled by [`dramatiq`](https://dramatiq.io),
and their docs can help with any advanced use.
