- **Client Nodes**: These make requests to analyze designs and retrieve analysis
  results once they finish.
  Client nodes will usually be running some optimization or search process.
- **Message Brokers**: These gather analysis requests from client nodes and
  distribute them to free worker nodes.
- **Worker Nodes**: These will perform analyses on designs and store the results
  somewhere accessible to the clients.
- **License Management**: Each worker node needs Creo to perform analysis, and
  a license for Creo must be made available somehow.
    - **License Server**: These can provide licenses to a number of worker nodes
      at once if provided with a floating license.
    - **Node-Locked Creo License**: This is a worker-specific, static license
      file that can be placed on a worker.
- **Component Corpus**: A corpus of component information that every
  worker needs in order to analyze designs.
    - **Corpus DB**: A graph database that the worker can use to look up
      component information.
    - **Static Corpus**: A static file containing a dump of the component corpus
      which is placed on each worker node.
- **Results Storage**: A file system, accessible to both worker nodes and
  clients, where analysis results (in individual zip files) are placed.
- **Results Backends**: These notify client nodes when their analysis requests
  are completed and where the output is in Results Storage.
