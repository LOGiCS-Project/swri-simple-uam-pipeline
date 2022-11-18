# Choosing a Deployment Topology

!!! error "Old stuff below"

<figure markdown>
  ![Project Components](../../assets/component-diagram.png)
  <figcaption>SimpleUAM Component Structure</figcaption>
</figure>

Client nodes, such as optimizers or search tools, should be able to queue
requests for distribution to worker nodes as they become available.
The results of those analyses, packaged as zip files, should then be made
available to the clients as they're completed.

The key components of a SimpleUAM deployment are:

--8<-- "docs/assets/deployment-components.md"

In order to form a complete SimpleUAM deployment some core requirements need to
be met:

--8<-- "docs/assets/deployment-rules.md"

With a SimpleUAM deployment meeting those requirements, a client nodes can
offload analysis jobs to a pool of workers though simple python and command
line interfaces.

## Choosing a Service Topology {#topology}

It's possible to distribute SimpleUAM components between multiple machines
in numerous ways that meet the given requirements.
Picking a topology, specifically the components that go on each individual
machine, tells you which installation steps are needed for that machine.

We'll look at two example topologies, one I use for (semi)local development
work and one for a potential production system.

<figure markdown>
  ![Project Components](../assets/development-setup.png)
  <figcaption>Development SimpleUAM System</figcaption>
</figure>

This development setup has a local machine and a single worker.
The local machine is set up so it can run a SimpleUAM client and so that any
code shared with a worker node can be edited in whatever manner the user is
comfortable with.
The worker node, running in a VM, then has all the other necessary components of
the service, including broker, license, and corpus.

The structure is a broad guideline and can be tweaked as needed.
For instance, if you're running windows you can just run all the components on
your local machine and use a stub message broker that will run analysis requests
as blocking calls.
Alternately, the worker node can be running on a server somewhere with a NFS
shared drive acting as the shared folder.

<figure markdown>
  ![Project Components](../assets/production-setup.png)
  <figcaption>Production SimpleUAM System</figcaption>
</figure>

The production service has significantly more going on.
There are one or more clients producing analysis requests, multiple workers
processing them, a Creo license server, a message broker, a results backend,
and results storage.

This setup can scale relatively easily while providing features like completion
notifications.
In fact this is the intended topology for the AWS instructions, with clients
either accessing the other components via a VPN or simply running directly
on the cloud.

Other topologies are also viable, for instance running a central graph database
for all the workers to share instead of relying on a local, static corpus.

The **most important part** of choosing a service topology is knowing what
component(s) are going to be running on each individual server or VM.
Given that one can just go through the instructions for each component on
a machine in sequence, repeating that process for each machine in the
deployment.

## Installation and Setup {#setup}

Setting up a SimpleUAM requires choosing how components are distributed between
the different machines in a deployment.

??? info "SimpleUAM Deployment Components"

    <figure markdown>
      ![Project Components](../assets/component-diagram.png)
      <figcaption>SimpleUAM Component Structure</figcaption>
    </figure>

    --8<-- "docs/assets/deployment-components.md"

The assignment between components and machines must follow the following rules.

??? info "Deployment Topology Rules"

    --8<-- "docs/assets/deployment-rules.md"

Then follow the steps for network setup once, and the machine setup instructions
for each machine in the deployment.

### Network Setup {#setup-net}

Once a deployment topology has been chosen, first set up the network so that:

- All workers and clients can communicate with the message broker and results
  backend.
- If using a license server, ensure it can communicate with all the workers.
- If using a global, shared corpus DB ensure it can communicate with all the
  workers.

If you are using AWS you can start with our instructions for setting up a
virtual private cloud (VPC).
It sets up a private subnet for non-client machines and a VPN and Network drive
for access to that private subnet.

- **[AWS (Network) Setup](aws-network.md)**

### Machine Setup {#setup-machine}

Installation for each machine requires following the other pages in this section
in order, skipping any that aren't relevant and always including general setup.
Try to setup machines with centralized functions, like the license server and
message broker, before the worker nodes.

- **[AWS (Instance) Setup](aws-instance.md)**
- **[General Setup](general.md)** *(Required)*
- **[Creo License Server](license_server.md)**
- **[Message Broker & Results Backend](broker.md)**
- **[Corpus DB](graph.md)**
- **[Static Corpus](corpus.md)**
- **[Worker Node](worker.md)**

Client nodes are less directly dependent on the SimpleUAM infrastructure and their
setup can skip directly to the corresponding section:

- **[Client Node](client.md)**

## Example Installation Orders {#setup-example}

Here are some worked examples of how to proceed through the setup process for
our example deployment topologies:

??? example "Example Local Development Deployment"

    <figure markdown>
      ![Project Components](../assets/development-setup.png)
      <figcaption>Development SimpleUAM System</figcaption>
    </figure>

    This deployment places a single worker node in a VM on a host machine.

    Initial setup would begin with:

    - Creating a Windows VM for the worker.
    - Ensuring that the VM can access the internet.
    - Ensuring the host machine has a route to the VM at some IP address.
    - Ensuring that a folder in the VM is mounted or mirrored on the host
      machine.

    Setup for the Worker VM would then go through the instructions for the
    relevant components:

    - **[General Setup](general.md)** *(Required)*
    - **[Message Broker & Results Backend](broker.md)**
    - **[Static Corpus](corpus.md)**
    - **[Worker Node](worker.md)**

    Finally, the host machine would go through the client instructions at:

    - **[Client Node](client.md)**

??? example "Example Production Deployment"

    <figure markdown>
      ![Project Components](../assets/production-setup.png)
      <figcaption>Production SimpleUAM System</figcaption>
    </figure>

    This deployment spreads work over multiple worker nodes within a subnet.

    Initial setup on AWS would follow **[AWS (Network) Setup](aws-network.md)**,
    otherwise it would begin with:

    - Creating the license server along with the broker, results, and worker
      nodes.
    - Creating the results storage and ensuring it's mounted on the worker
      nodes.
    - Ensure that the workers have a route to the license server and the message
      broker.

    The license server would go through the following, adding the AWS step if
    needed:

    - **[AWS (Instance) Setup](aws-instance.md)**
    - **[General Setup](general.md)** *(Required)*
    - **[Creo License Server](license_server.md)**

    The message broker would likewise go through:

    - **[AWS (Instance) Setup](aws-instance.md)**
    - **[General Setup](general.md)** *(Required)*
    - **[Message Broker & Results Backend](broker.md)**

    Similarly, each worker node would go through:

    - **[AWS (Instance) Setup](aws-instance.md)**
    - **[General Setup](general.md)** *(Required)*
    - **[Static Corpus](corpus.md)**
    - **[Worker Node](worker.md)**

    !!! Tip "A clone of a working worker should be fully functional out of the box."

    Finally, each client would go through the client instructions at:

    - **[Client Node](client.md)**
