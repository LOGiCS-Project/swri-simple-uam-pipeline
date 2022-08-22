- There must be one, and only one, message broker.
    - The broker must be accessible over the network to all worker and client nodes.
- There needs to be at least one configured, running worker node to run analyses.
    - Each worker node needs to have a Creo license, either through a
      node-locked license or a connection to a Creo license server.
    - Each worker node needs to have access to a component corpus, either through
      an initialized corpus DB or a static corpus file.
- There must be a results storage accessible to all the worker and client nodes.
    - The results storage should be a directory where workers can place files
      which are then made accessible to all the clients.

        ??? Tip "Possible Storage Mechanisms"
            Generally the results store will be a mounted network file share or
            local folder, but could also be:

            - A network file system mounted on workers and clients. *(Default)*
            - A local folder, if both worker and client are on the same machine.
            - [rsync](https://rsync.samba.org/)+[cron](https://en.wikipedia.org/wiki/Cron)
            - [Dropbox](https://www.dropbox.com/)
            - [Google Drive](https://www.google.com/drive/)
            - [S3 Drive](https://www.nsoftware.com/drive/s3drive/)
            - Anything that looks like a filesystem directory to both the worker
              and the client.

- In order for clients to receive analysis completion notifications there must
  be a single, unique results backend.
    - This backend must be accessible over the network to all worker nodes and
      any client that wants to receive notifications.

        !!! Tip "A results backend is optional and simply polling the results storage is perfectly viable."
