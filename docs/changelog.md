# Changelog

## v0.1.0 {#v0.1.0}

- Added notes to docs on how to use UNC format for FSx drives.
- Added `python-dateutil` and `gremlinpython` to required pip packages.
- Fixed bug preventing API docs from being generated.
- Fixed bug where supplying a `paths.conf.yaml` resulted in all commands
  hanging.
- Added `start_hook` and `stop_hook` fields to the service sections in
  `craidl.conf.yaml` and `d2c_worker.conf.yaml`.
  Setting these to a non-null string will run the string as a command either
  before or after the service runs.
- Updated various SWRi repositories to their latest versions.
- Updated the static corpus to match SWRi's latest corpus.
- Made `pdm run craidl corpus.install` more idempotent by removing prompt
  for deletion of old corpus and just creating a backup by default.
- User metadata, when provided through any of the direct2cad interfaces
  (local and remote, programmatic and CLI) will now end up in the `'user_metadata'`
  field of '`metadata.json`' rather than being placed at the root.
- Fixed bug where error handling during a session threw another error, keeping
  any information from getting to the user.


### Deployment Update Instructions (from earlier versions) {#v0.1.0-dep-update}

- Update worker pip-pkgs:
    - Run `pdm run setup-win worker.pip-pkgs`
- Add or modify the worker service's pre or post hooks:
    - In `d2c_worker.conf.yaml` set the fields for `service.pre_hook` and
      `service.post_hook` to a command to run before or after the worker process.
    - Run `pdm run suam-worker service.configure`
- If using the default UAM Workflows or Direct2Cad repos, update them:
    - Run `pdm run d2c-workspace setup.reference-workspace`
- If generating a static corpus from the default GraphML dump, update it:
    - Run `pdm run craidl corpus.install`
        - Note that the underlying repo has changed and you will need to confirm
          use of an insecure password if ISIS SSH keys aren't configured.
    - Run `pdm run craidl stub-server.configure`
    - While running process `pdm run craidl stub-server.run`
        - Run `pdm run craidl static-corpus.generate`
    - Run `pdm run craidl static-corpus.install`


### User Update Instructions (from earlier versions) {#v0.1.0-user-update}

- Update code and workflows to reflect that user metadata isn't placed at
  the root of a results archive's '`metadata.json`' file anymore.
  Instead user metadata will be in the `'user_metadata'` field of those
  files.
