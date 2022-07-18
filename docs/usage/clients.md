# SimpleUAM Client Nodes

Client nodes create designs in the SRI format and send those designs to a
SimpleUAM deployment to be processed.

## Configuration Instructions {#config}

See [here](../../setup/client/#broker) for instructions on how to set up a client
node.

!!! todo "TODO: Details"

## Client Tasks via CLI {#CLI}

See [here](../../setup/client#test) for basic interface.

!!! todo "TODO: Details"

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
