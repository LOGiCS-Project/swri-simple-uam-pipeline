# SimpleUAM Installation Guide

SimpleUAM helps process UAV and UAM designs using SWRi's Direct2Cad analysis
pipeline.
It focuses on minimizing the difficulty of setting up and using SWRi's tools
by making the surrounding infrastructure modular and automated.

The most important split SimpleUAM makes is between clients and a
worker deployment:

- **SimpleUAM Clients:** TODO calls to deloyment for swri ops, lightweight,
  OS agnostic

- **SimpleUAM Worker Deployment:** TODO processes calls as needed, returns results
  to clients, Windows req (due to creo)

TODO :: Can be structured in many ways incl. single box, fixed size, autoscales

TODO :: General outline of install: If client, then follow instr for client
if worker, figure out deployment then follow inst
if both do worker then client

TODO :: Link to Installation Notes


<!-- Client nodes, such as optimizers or search tools, should be able to queue -->
<!-- requests for distribution to worker nodes as they become available. -->
<!-- The results of those analyses, packaged as zip files, should then be made -->
<!-- available to the clients as they're completed. -->

<!-- The key components of a SimpleUAM deployment are: -->

<!-- --8<-- "docs/assets/deployment-components.md" -->

<!-- In order to form a complete SimpleUAM deployment some core requirements need to -->
<!-- be met: -->

<!-- --8<-- "docs/assets/deployment-rules.md" -->

<!-- With a SimpleUAM deployment meeting those requirements, a client nodes can -->
<!-- offload analysis jobs to a pool of workers though simple python and command -->
<!-- line interfaces. -->
