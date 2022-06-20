# Craidl Tools

- Modified from code privded by sri.
- Exists to support a single step needed by direct2cad analysis pipeline
    - gen_info_file
- has infra for
    - downloading and installing a graphml corpus
    - keeping track of a component information corpus
    - keeping track of an example design corpus
        - setup, sri download, and cleanup
    - generating a static corpus from a running corpus db
    - using either a corpus db to a static corpus to
      generate the info files for a design.
        - command line args
- Also config file breakdown?

!!! warning "Section Incomplete"

??? todo "reqs"
    - Craidl:
        - Run and use CorpusDB stub server
        - Use the generated static corpus
        - Using / generating either type of corpus

- Tools can use graph server corpus or static file for 'gen_info_files'
- Specify which through config files (`craidl.conf.yaml`)
- Server:
    - Needs `.graphml` corpus from swri.
    - Can download UAM corpus from repo or install user provided
- Static Corpus:
    - Can copy from this repo's data
    - Can generate from running graph server
- Examples:
    - Keeps a directory of example designs
    - Can download examples from trinity-craidl repo
    - Can let user add as needed.

### Install Engineering Corpus

**Option 1**: Download default from athens-uav-workflows

- In admin powershell at `<repo-root>`.
- Download athens-uav-workflows repo and get `all_schema_uam.graphml`
    - Run: `pdm run craidl corpus.download`
    - Follow prompts, enter git.isis.vanderbilt.edu credentials if needed.
- Install corpus to default location.
    - Run: `pdm run craidl corpus.install`
    - Default parameters will use downloaded corpus.

**Option 2**: Install from provided file

- In admin powershell at `<repo-root>`.
- Install user provided corpus from `<corpus-loc>`.
    - Run: `pdm run craidl corpus.install --corpus=<corpus-loc>`

### Configure Corpus Server

- In admin powershell at `<repo-root>`.
- Craidl settings file:
    - Examine loaded config with `pdm run suam-config print --config=craidl -r`
    - Server will use `stub_server.host` and `stub_server.port` by default.
- Install and configure graph server
    - Run: `pdm run craidl stub-server.configure`
    - Will use configured host, port, and graphml corpus.

### Run Corpus Server

- Once configured open admin powershell at `<repo-root>`.
- Run the graph server as a process.
    - Run: `pdm run craidl stub-server.run`
    - Note that this isn't a service, the server will stop if you close the
      terminal.

### Install Static Corpus

Generating the info files for a design is very slow when using a server so
we provide an option to use a static JSON corpus.

**Option 1**: Use the provided static corpus from this repo.

This is the corpus for `all_schema_uam.graphml` generated in June '22.

- Once configured open admin powershell at `<repo-root>`.
- Install the corpus provided with this repo.
    - Run: `pdm run craidl static-corpus.copy`

**Option 2**: Use a user provided static corpus.

- Once configured open admin powershell at `<repo-root>`.
- Install a user provided corpus from `<static-corpus-loc>`
    - Run: `pdm run craidl static-corpus.copy --input=<static-corpus-loc>`

**Option 3**: Generate from the graph server.

This will generate a static corpus from a running graph server, using whatever
corpus it was configured with.

- Make sure a graph server is running at the configured location.
    - Examine loaded config with `pdm run suam-config print --config=craidl -r`
    - Server should be running at `server_host` on port `server_port`
    - Defaults would use a local stub server.
- Generate the static corpus from that server.
    - Run: `pdm run craidl static-corpus.generate`

With default settings the corpus generation and the stub server can hang
intermittently, so the generation command periodically saves its progress.
Just rerun the command (with the same settings) and it will resume generating
the corpus from the last saved cluster of components.

### Generate Design Info Files

The `gen-info-files` command will let you generate the files the direct2cad
pipeline uses.

```powershell
PS D:\simple-uam> pdm run craidl gen-info-files --help
Usage: craidl.EXE [--core-opts] gen-info-files [--options] [other tasks here ...]

Docstring:
  Generates the info files for a given design.

  Arguments:
    design: '.json' with design information. Default: 'design_swri.json'
    output: The output **directory** in which to place the files.
      Default: cwd
    copy_design: Do we copy the input design to the output directory?
      Default: False

    static: The static '.json' corpus to use when generating the files.
      Mutually exclusive with host and port. Default: As configured
    host: The hostname of the corpus server to use when generating the files.
      Mutually exclusive with static. Default: As configured
    port: The port of the corpus server to use when generating the files.
      Mutually exclusice with static. Default: As configured

Options:
  -c, --copy-design
  -d STRING, --design=STRING
  -h STRING, --host=STRING
  -o STRING, --output=STRING
  -p STRING, --port=STRING
  -s STRING, --static=STRING
```

The default settings for `static`, `host`, and `port` are based on the values
in `craidl.conf.yaml`.
