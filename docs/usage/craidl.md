# Craidl Tools

The craidl module and CLI tool are designed to support generating a info
files for a design from SRI's compressed representation.
These info files are an expanded version of a design that pulls in specific
component information from the corpus so that SWRi's direct2cad pipeline can
process it.
The core of this is based on work by SRI, albeit heavily modified for a number
of reasons.

As implemented the Craidl module in SimpleUAM has a few major components/concepts:

- **Corpus**: This is the SWRi provided `.graphml` file that contains
  information on components and designs within the current challenge problem.
- **Stub Server**: A small graph server that can serve the corpus to tools which
  expect to access it via Gremlin graph queries.
- **Static Corpus**: This is component information from the corpus extracted into
  a much smaller, more efficient, distributable form.
- **Examples**: This is a list of designs, in SRI's design representation, that
  can serve as a pool of seeds or examples for testing.
  This should probably be called the 'static design corpus' or something.

The basic install procedure can be found [here](../../setup/graph).
This page covers other things.

## Updating Craidl {#update}

When the corpus or various config files change you'll need to propagate those
changes to the stub-server.

The easiest way to do this is to go through the install instructions again.
The operations are all functionally idempotent and make backups of things they
would overwrite.

Note that `corpus.install` must be run to update the active corpus before
running `stub-server.configure` which copies that corpus to the appropriate
location for the stub server.

## Running `gen_info_files` {#gen-info-files}

The craidl CLI allows you to generate the direct2cad info files directly
using either a static corpus or a corpus DB.
This uses the `craidl.conf.yaml` config information and the `gen-info-files`
sub-command.

Run the following for details on the sub-command:
```bash
pdm run craidl gen-info-files --help
```

This is a functional standalone command that doesn't require additional setup
of workspaces or a worker node.

## Working With Examples {#examples}

We can store a set of examples designs in a local corpus.
This is mainly for convenience during testing as there isn't much call for such
a store otherwise.

The example store contains individual folders for each example's
`design_swri,json` file.

The main commands to work with examples are all of the form:
```bash
pdm run craidl <sub-command> <args>
```

The main sub-commands are:

- **`examples.dir`**: Prints the directory where examples are stored.
- **`examples.list`**: Lists all available examples.
- **`examples.add`**: Will add an example to the example directory.
- **`examples.clean`**: Deletes all stored examples.
- **`examples.sri.install`**: Downloads and installs examples from the
  trinity-craidl repo.

Use the `--help` argument to get more details on flags and parameters.
