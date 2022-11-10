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
