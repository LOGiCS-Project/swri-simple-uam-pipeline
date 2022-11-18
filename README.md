# SimpleUAM : Tools for SWRi's UAV and UAM Workflow

SimpleUAM is a set of python libraries and command-line tools for working with
SWRi's pipeline for UAV development.
Its main goals are to make the SWRi pipeline easy to deploy and wrap it with
convenient interfaces for external tools.

## Key Features

- **SWRI's *full* direct2cad pipeline:** SimpleUAM allows you to run the
  direct2cad pipeline with arbitrary designs, custom study parameters, and
  even modified FDM executables.
- **Easy custom autopilots:** Users can provide their custom autopilot
  source code, which will be automatically built into an FDM executable suitable
  for all the other operations SimpleUAM supports.
- **Command line and Python interfaces:**
  We provide multiple, easy to use interfaces for both local and remote
  processing of UAV/UAM designs.
  Python bindings take case of the common case, but our CLI can be used
  both manually and by any language capable of file IO and terminal commands.
- **Simple task queue architecture:**
  SimpleUAM is built around the humble task queue.
  Clients submit jobs to one or more workers, getting results back as they're
  completed.
  It's a model that's easy to integrate into existing analysis and
  optimization pipelines whether they have blocking or non-blocking semantics.
- **Deploy locally or on the cloud:**
  Because SimpleUAM is organized around interchangable infrastructure
  components, it can be set up on a local VM, a handful of servers, or as an
  highly-available, auto-scaling cloud service.
- **Highly automated installation:**
  Our installation process tries to automate every step that doesn't need user
  input and makes each step as idempotent as possible.
  This minimizes room for user error and makes fixing most of those errors as
  simple as repeating the last few steps.

**See [Github Pages](https://logics-project.github.io/swri-simple-uam-pipeline/)
for more details...**
