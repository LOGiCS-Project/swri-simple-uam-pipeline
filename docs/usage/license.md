# License Server

The license server will provide floating licenses to Creo on each of your worker
nodes.

## Updating Creo License {#update-creo}

> Update the creo license on a running server with a new one.

### Prerequisites {#update-creo-prereqs}

- Have your new license available at `<creo-license.file>`

### Import to Flexnet Server {#update-creo-import}

- Open the web interface:
    - Start Menu -> PTC -> Flexnet Admin Web Interface

- Open the administration page:
    - **User:** admin
    - **Pass:** `<creo-license.flexnet-password>`

- Open the 'Vendor Deamon Adminstration' page:
    - Click 'Import License':
        - **License File From Your Local Machine**: `<creo-license.file>`
        - **Overwrite License File on License Server**: Yes

- Reboot the server.

- Open the web interface:
    - Start Menu -> PTC -> Flexnet Admin Web Interface

- Open the 'Vendor Deamon Adminstration' page:
    - Click 'Administer' for the 'ptc_d' license
    - Click 'Start'
