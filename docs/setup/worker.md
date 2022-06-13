# Worker Node Setup

A worker can analyze designs on behalf of clients and requires access to a
license server and a broker for most tasks.

Ensure you have a `<license-server-ip>`, `<broker-ip>`, and `<broker-port>`.

Ensure you've completed the steps in [General Setup](general.md) already.

### Install Dependencies

Install utilities like wget and rsync.

- Open an admin powershell to `<repo-root>`:
    - Run: `pdm run setup-win install.worker-deps`

### Install Creo

Get license information, optionally installing the license server locally.

- Have your license information ready:
    - Get your mac address (for generating licenses):
        - Run: `pdm run setup-win mac-address`
    - If using a local license, have the license file for the above mac
      address downloaded somewhere convenient.
    - If using a license server, have `<license-server-ip>` at hand.

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

**Configure component corpus [here](../usage/craidl.md)...**<br/>
**Configure and use local analysis pipeline [here](../usage/workspaces.md)...**<br/>
**Configure and use remote analysis pipeline [here](../usage/workers.md)...**
