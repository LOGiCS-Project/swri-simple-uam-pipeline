# SimpleUAM : Tools for SWRi's UAV and UAM Workflow

SimpleUAM is a set of python libraries and command-line tools for working with
SWRi's pipeline for UAV development.
Its main goals are to make the SWRi pipeline easy to deploy and wrap it with
convenient interfaces for external tools.

## Organization

SimpleUAM organizes its major components into nodes, each of which perform
some basic task:

  - **Clients**: Make requests for UAV/UAM design analysis.
  - **Message Broker**: Distribute analysis requests from clients to available
    workers.
  - **Workers**: Analyze designs with SWRi's pipelines.
  - **Engineering Corpus**: Provide component and design data for use during analysis.
  - **License Servers**: Provide floating Creo licenses to workers.
  - **Results Storage**: Store the results of design analyses.

These nodes aren't tied to specific machines and can all happily coexist on a
single computer or support multiple servers cooperating on each task.

This project provides support for versions of all of these nodes including
setup scripts and python libraries for interacting with them.

## Links

 - [**Install Instructions**](setup/intro.md)
