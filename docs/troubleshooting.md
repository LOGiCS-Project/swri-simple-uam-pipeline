# Troubleshooting

- Permissions errors when using `pdm` to manage the project, like the following:

  ```
  [PermissionError]: [Errno 13] Permission denied: 'E:\\simple_uam\\pdm.lock'
  ```

  Can often be solved by clobbering the `pdm` and `python` caches and
  reinstalling the dependencies:

  ```bash
  $ rm -rf __pypackages__ pdm.lock .pdm.toml
  $ pdm install
  ```

- Errors involving missing non-SimpleUAM modules like:

  ```bash
  $ pdm run craidl
  Error processing line 1 of E:\simple_uam\__pypackages__\3.10\lib\simple_uam.pth:

    Traceback (most recent call last):
      File "C:\Python310\lib\site.py", line 186, in addpackage
        exec(line)
      File "<string>", line 1, in <module>
      File "E:\simple_uam\__pypackages__\3.10\lib\__editables_simple_uam.py", line 1, in <module>
        from editables.redirector import RedirectingFinder as F
    ModuleNotFoundError: No module named 'editables'

  Remainder of file ignored
  Traceback (most recent call last):
    File "C:\Python310\lib\runpy.py", line 196, in _run_module_as_main
      return _run_code(code, main_globals, None,
    File "C:\Python310\lib\runpy.py", line 86, in _run_code
      exec(code, run_globals)
    File "E:\simple_uam\__pypackages__\3.10\Scripts\craidl.EXE\__main__.py", line 4, in <module>
    File "E:\simple_uam\simple_uam\tools\craidl\cli.py", line 15, in <module>
      from simple_uam.util.invoke import Collection, InvokeProg, task
    File "E:\simple_uam\simple_uam\util\invoke\__init__.py", line 1, in <module>
      from .program import InvokeProg
    File "E:\simple_uam\simple_uam\util\invoke\program.py", line 1, in <module>
      from invoke import Program
  ModuleNotFoundError: No module named 'invoke'
  ```

  Can often be solved by running the following in `<repo_root>`:

    1. Ensuring that `pip` and `pdm` are updated:
      ```bash
      $ python -m pip install -u pip
      $ python -m pip install -u pdm
      ```

    1. Clobbering the `pdm` and `python` caches:
      ```bash
      $ rm -rf pdm.lock .pdm.toml __pypackages__
      ```

    1. Ensuring that permissions are open:
      ```bash
      $ chmod 777 -Rv ./
      ```

    1. Disabling `pdm`'s use of `venv`:

      ```bash
      $ pdm config python.use_venv
      ```

      !!! Note "This is global and affects all `pdm` projects on the system."

    1. Reinstalling the project with `pdm`:
      ```bash
      $ pdm install
      ```

- Errors connecting to the broker through a VPN:

  ```bash
   return self.broker.enqueue(message, delay=delay)
  File "/usr/local/lib/python3.10/site-packages/dramatiq/brokers/redis.py", line 186, in enqueue
    self.do_enqueue(queue_name, message.options["redis_message_id"], message.encode())
  File "/usr/local/lib/python3.10/site-packages/dramatiq/brokers/redis.py", line 278, in do_dispatch
    self._max_unpack_size(),
  File "/usr/local/lib/python3.10/site-packages/dramatiq/brokers/redis.py", line 255, in _max_unpack_size
    cls._max_unpack_size_val = DEFAULT_LUA_MAX_STACK or self.scripts["maxstack"]()
  File "/usr/local/lib/python3.10/site-packages/redis/commands/core.py", line 5710, in __call__
    return client.evalsha(self.sha, len(keys), *args)
  File "/usr/local/lib/python3.10/site-packages/redis/commands/core.py", line 5095, in evalsha
    return self._evalsha("EVALSHA", sha, numkeys, *keys_and_args)
  File "/usr/local/lib/python3.10/site-packages/redis/commands/core.py", line 5079, in _evalsha
    return self.execute_command(command, sha, numkeys, *keys_and_args)
  File "/usr/local/lib/python3.10/site-packages/redis/client.py", line 1235, in execute_command
    conn = self.connection or pool.get_connection(command_name, **options)
  File "/usr/local/lib/python3.10/site-packages/redis/connection.py", line 1387, in get_connection
    connection.connect()
  File "/usr/local/lib/python3.10/site-packages/redis/connection.py", line 617, in connect
    raise ConnectionError(self._error_message(e))
  redis.exceptions.ConnectionError: Error 8 connecting to swri-cloud-broker.iquigz.clustercfg.memorydb.us-west-2.amazonaws.com:6379. nodename nor servname provided, or not known.
  ```

  Probably a DNS resolution error, where it can't lookup the address by DNS name. Check VPN settings.

  See: https://aws.amazon.com/premiumsupport/knowledge-center/client-vpn-how-dns-works-with-endpoint/

  Also try replacing a DNS lookup in your broker with an IP address
