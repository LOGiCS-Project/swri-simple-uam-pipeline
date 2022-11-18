# Todo

## Docs

- [ ] Reorg Overview
    - [x] Add key features section
    - [ ] Add separate hooks for client or worker install.
    - [ ] Add some other pointers to key sections of the docs.
    - [ ] Separate out the readme and overview pages.
- [ ] Clean up general install section
    - [ ] Section on basic organization
    - [ ] Section on notes
      - [ ] trim and consolidate notes on config tool
      - [ ] Fine grained links to config pages.
- [ ] Clean up all install phases
    - [ ] "Option ..)" and "(Reccomended)"
    - [ ] format
        - [ ] explanation of why in quotes
        - [ ] general instructions as plain text
        - [ ] specific steps as bullets
- [ ] Separate "Worker install" section
    - [ ] Section for service topology
    - [ ] Separate out section for provisioning deployment nodes
    - [ ] Number all operations
    - [ ] Add operations for FDM steps
    - [ ] Explicit section for "Make client bundle"
    - [ ] Section for autoscaling
- [ ] Separate "Client install" section
    - [ ] Number all operations
    - [ ] Add section for "Using client bundle"
        - [ ] Various convenient client instruction snippets to be used as
          directed.
- [ ] Configuration
    - [ ] Format
    - [ ] General Model
    - [ ] Command Line Tools
    - [ ] Separate Pages for Each Config File
- [ ] Corpus Management
    - [ ] Model (graphml vs. static)
    - [ ] Command line tool
    - [ ] Task "Loading corpus"
    - [ ] Task "Using stub server"
    - [ ] Task "Building static corpus"
    - [ ] Task "Downloading Examples"
- [ ] Task Sections
    - [ ] Section "FDM Build"
        - [ ] Description
        - [ ] Inputs & Output
            - [ ] Inputs & Format
            - [ ] Key Archive File Outputs
        - [ ] CLI Interface
        - [ ] Programmatic Interface
    - [ ] Section "FDM Eval"
        - [ ] Description
        - [ ] Inputs & Output
            - [ ] Inputs & Format
            - [ ] Key Archive File Outputs
        - [ ] CLI Interface
        - [ ] Programmatic Interface
    - [ ] Section "Direc2Cad"
        - [ ] Description
        - [ ] Inputs & Output
            - [ ] Inputs & Format
            - [ ] Key Archive File Outputs
        - [ ] CLI Interface
        - [ ] Programmatic Interface
- [ ] Section on "design"
    - [ ] CLIs as going from input to metadata w/ local as direct, and client as
      piped.
    - [ ] Workspace concepts.
- [ ] Non-Python / CLI Interfaces
- [ ] Add changelog
    - [ ] Migrate for workers & servers
    - [ ] Migrate for clients (CLI & Programmatic)
- [ ] regenerate configs and stuff
    - [ ] "print_all.conf.yaml"
    - [ ] "print_all_resolved.conf.yaml"
- [ ] Update the diagrams
    - [ ] Use configuration json to re-theme existing diagrams.
    - [ ] Generate both light and dark versions of each diagram.
    - [ ] Update all embeds to swap diagrams out based on theme

# Contributing

- [ ] Logging
- [ ] Using docs and stuff
- [ ] Misc management cmds
- [ ] Repo Management
- [ ] Open requests

# Better Autoscaling Metric

- [ ] Use product of free capacity for CPU & each workspace.
- [ ] `msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi`
- [ ] https://awstip.com/auto-scaling-with-custom-metrics-477fb67e6814
- [ ] https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/install-CloudWatch-Agent-commandline-fleet.html
- [ ] https://www.techtarget.com/searchcloudcomputing/tutorial/How-to-create-EC2-custom-metrics-with-Amazon-CloudWatch
