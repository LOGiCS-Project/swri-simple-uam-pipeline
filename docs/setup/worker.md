# Worker Node Setup

A worker can analyze designs on behalf of clients and requires access to a
license server and a broker for most tasks.

### Prerequisites

- [General Setup](general.md) has been completed.
- SSH keys or credentials for `git.isis.vanderbilt.edu`
- A broker running at `<broker-ip>` and `<broker-port>`

### Install Dependencies

Install utilities like wget and rsync.

- Open an admin powershell to `<repo-root>`:
    - Run: `pdm run setup-win install.worker-deps`

### Get License Information

**Option 1:** License Server

- Have a license server running at `<license-server-ip>` on port `<license-server-port>`.

**Option 2:** Static Creo License

- Get your mac address (for generating licenses):
    - Run: `pdm run setup-win mac-address`
- If using a local license, have the license file for the above mac
  address downloaded somewhere convenient.

### Install Creo

Downloads and installs PTC Creo 5.6.

- Open an admin powershell to `<repo-root>`:
  - Run: `pdm run setup-win worker.creo`
  - Read instructions in terminal and hit enter when ready.
  - Follow installer prompts until done.

Fix some minor usability issues.

- If on Windows Server 2019 you can disable the IE Enhanced Security popups
  that open whenever Creo starts.
    - Run: `pdm run setup worker.disable-ieesc`

### Install Creopyson

- Prepare to connect to git.isis.vanderbilt.edu:
    - Install SSH keys for git.isis.vanderbilt.edu
    - **Or** have credentials ready for prompt.
- Open an admin powershell to `<repo-root>`:
    - Run: `pdm run setup-win worker.creopyson`
    - Follow prompts.

### Configure Corpus Settings

!!! todo
    - corpus / craidl settings
    - have static corpus installed or corpus db running
    - see usage craidl for deets

### Configure Records Dir

!!! todo
    - d2c_workspace set records_dir
    - see usage workspaces for deets

### Configure Worker Settings

!!! todo
    - set broker
    - set process limit
    - see usage worker for deets

### Run Worker Node

- Once configured open admin powershell at `<repo-root>`.
- Run the graph server as a process.
    - Run: `pdm run d2c-worker worker.run`
    - Note that this isn't a service, the server will stop if you close the
      terminal.

!!! todo
    goto client
