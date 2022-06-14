# Direct2Cad Workspace

A workspace is an environment (i.e. folder) set up so that SWRi's direct2cad
pipeline can run within it.

Each workspace has session where commands are run and any changes from a
clean workspace (like output cad or data files) are saved to a zipfile and
moved to a storage directory.

You can run these sessions locally through code or console commands.

There are 3 provided sessions:

- `tasks.start-creo`: Will start Creo on the worker. Exists for debug
  purposes. Other sessions that need Creo running can start it themselves.
- `tasks.gen-info-files`: Will generate info files using the configs in
  `d2c_workspace.conf.yaml` and package them in a records archive.
- `tasks.process-design`: Runs the direct2cad pipeline on the provided
  design and generates a record archive with the result.

These tasks only function on a worker node set up as [here](../setup/worker.md).

In addition before running any sessions, a reference workspace must be set up
to serve as the basis for any 'live' workspaces.

### Setup Reference Workspace

- In admin powershell at `<repo-root>`.
    - Run: `pdm run d2c-workspace setup.reference-workspace`

### Manage Configuration Files

The configs in `<config-dir>/d2c_workspace.conf.yaml` control workspace
locations, the settings for craidl's `gen_info_files`, and where records are
stored.

- Examine loaded config with `pdm run suam-config print --config=d2c_workspace -r`

See [here](config.md) for more information on config files.

!!! important
    Make sure the `records_dir` is set how you want. That is where all the
    results archives will go.
    If you don't want it to be a sub-directory of `workspaces_dir` make sure
    `records_dir` is an absolute path.

### Manage Workspaces

Get the cache directory for these workspaces.

- In admin powershell at `<repo-root>`.
    - Run: `pdm run d2c-workspace manage.cache-dir`

Get the root directory of the reference workspace and the live workspaces.

- In admin powershell at `<repo-root>`.
    - Run: `pdm run d2c-workspace manage.cache-dir`

Get the records directory for these workspaces. This is where the zip files with
data from each session will go.

- In admin powershell at `<repo-root>`.
    - Run: `pdm run d2c-workspace manage.records-dir`

Prune the records directory by deleting old records until only the configured
maximum are present. It will not delete records that are newer than the
configured `min_staletime`.

- In admin powershell at `<repo-root>`.
    - Run: `pdm run d2c-workspace manage.prune-records`

Delete any file system locks that might have gotten left behind. These
usually prevent multiple processes from taking control of the same live
workspace.

- In admin powershell at `<repo-root>`.
    - Run: `pdm run d2c-workspace manage.delete-locks`

### Run `gen_info_files` Session

This requires [craidl](craidl.md) to be properly set up including having a
static corpus or graph server set up as needed.

```powershell
PS D:\simple-uam> pdm run d2c-workspace tasks.gen-info-files --help
Usage: pdm run d2c-workspace [--core-opts] tasks.gen-info-files [--options]

Docstring:
  Will write the design info files in the specified
  workspace, and create a new result archive with only the newly written data.
  The workspace will be reset on the next run.

  Arguments:
    input: The design file to read in.
    workspace: The workspace to run this operation in.
    output: File to write output session metadata to, prints to stdout if
      not specified.

Options:
  -i STRING, --input=STRING
  -o STRING, --output=STRING
  -w STRING, --workspace=STRING
```

### Run `start_creo` Session

```powershell
PS D:\simple-uam> pdm run d2c-workspace tasks.start-creo --help
Usage: pdm run d2c-workspace [--core-opts] tasks.start-creo [--options]

Docstring:
  Start creo within the specified workspace, whichever's available if
  none.

  Arguments:
    workspace: The workspace to run this operation in.
    output: File to write output session metadata to, prints to stdout if
      not specified.

Options:
  -o STRING, --output=STRING
  -w STRING, --workspace=STRING
```

### Run `process_design` Session

This requires [craidl](craidl.md) to be properly set up including having a
static corpus or graph server set up as needed.

```powershell
PS D:\simple-uam> pdm run d2c-workspace tasks.process-design --help
Usage: pdm run d2c-workspace [--core-opts] tasks.process-design [--options]

Docstring:
  Runs the direct2cad pipeline on the input design files, producing output
  metadata and a records archive with all the generated files.

  Arguments:
    design: The design file to read in.
    workspace: The workspace to run this operation in.
    output: File to write output session metadata to, prints to stdout if
      not specified.

Options:
  -i STRING, --input=STRING
  -o STRING, --output=STRING
  -w STRING, --workspace=STRING
```