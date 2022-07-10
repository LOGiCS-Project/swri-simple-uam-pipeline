# Creo License Server Setup

This sets up a floating Creo license that worker nodes can use.
A machine or VM with direct access can use a node-locked Creo license instead.
However if you need to access the VM through RDP a floating license is required.

### Prerequisites {#prereqs}

- [General Setup](general.md) has been completed.
- The IP of this machine is saved as: `<license-server.ip>`

### Get License File {#license}

> Get the Host ID and License File.

- Open an admin powershell to `<repo-root>`.
- Get the Host ID / mac address for this machine:
  ```bash
  pdm run setup-win mac-address
  ```
- Save the result as `<license.host-id>`.
- Get the Creo floating license for `<license.host-id>`.
- Place the license file at `<license.file>`, somewhere on this machine.

### Install Dependencies

> Install utilities like wget and rsync.

- Open an admin powershell to `<repo-root>`.
- Install necessary dependencies:
  ```bash
  pdm run setup-win install.license-deps
  ```

### Install Flexnet Server

> Flexnet server is one of the options for hosting the license server and has
> been reasonably easy to use.

- Open an admin powershell to `<repo-root>`.
- Download and run the installer:
  ```bash
  pdm run setup-win license-server.flexnet
  ```

- Wait for installer to download and hit enter when prompted.
- Follow GUI installer's prompts until done, including providing `<license-file>`
  when asked for it.

### Open Required Ports

> Open the relevant ports up so instances of Creo on the worker nodes can
> connect.

!!! Note
    If you only intend to use Creo locally, on the same machine as the license
    server then you don't need to open any ports up.

#### **Option 1:** Open only port 7788.

The instructions for this are too configuration specific for us to provide.

#### **Option 2:** Disable license server firewalls entirely.

We can't provide general instructions for this step but if you're using
Windows Server 2019 you can use one of our scripts.

!!! warning
    This is not secure at all. Do not do this if the license
    server is at all accessible from public or untrusted computers.

- Disable the Windows Server 2019 firewall:
  ```bash
  pdm run setup-win license-server.disable-firewall
  ```

**Note:** This might work with other versions of Windows but that hasn't been
tested.

### Configure and Start Server

> Configure the server with a new admin password and start it.

- Open the web interface:
    - Start Menu -> PTC -> Flexnet Admin Web Interface

- Open the administration page:
    - **Default User:** admin
    - **Default Pass:** admin

- Change the password:
    - **Old Pass:** admin
    - **New Pass:** `<flexnet-password>`

- Start the server:
    - Administration -> Server Configuration -> Start Server

The server should now automatically start on boot.
