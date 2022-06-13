# SimpleUAM Configuration System

SimpleUAM uses a set of config files and a helper utility (`suam-config`) to
configure the operation of different features.

 - Config files are YAML with a defined schema.
 - Files are looked for in a fixed directory (find it with `pdm run suam-config dir`)
 - Each file corresponds to a module in `simple_uam.util.config`.

### Find Config Directory

!!! todo
    `pdm run suam-config dir`

### List Config Files

!!! todo
    `pdm run suam-config list-files`

### Print Current Config State

!!! todo
    W/ Interpolants: `pdm run suam-config print -a`
    Fully Resolved: `pdm run suam-config print -ar`

### Write Out Config Files

Writes commented out config files to correct location.

!!! todo
    `pdm run suam-config write`

### Config Interpolation

!!! todo
    Based on OmegaConf.
    find interp keys w/ `pdm run suam-config list-keys`
