# Direct2Cad Worker

A worker will listen for tasks from a message broker and then run those tasks.

### Configure Worker Settings

- Configure the message broker and other settings in
  `<config-dir>/d2c_worker.conf.yaml`.
- Examine loaded config with `pdm run suam-config print --config=d2c_worker -r`

### Run Worker Process

A worker node, which listens to a broker and performs tasks as requests come
in must have been set up as [here](../setup/worker.md).

- Make sure that direct2cad workspaces have been properly set up on this node
  as described [here](workspaces.md).
    - That code is what the worker process uses to evaluate a task, so if it
      doesn't function locally it won't function when a remote client asks.
- Make sure that a message broker is running at the configured host and port.

Actually run the worker process.

- In admin powershell at `<repo-root>`.
    - Run: `pdm run d2c-worker worker.run`

Note that this is a process not a service. If it shuts down it needs to be
restarted.

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
