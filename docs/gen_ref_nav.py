"""Generate the code reference pages and navigation."""

from pathlib import Path
import os
import mkdocs_gen_files

nav = mkdocs_gen_files.Nav()

packages = {
    "simple-uam": {"src_dir": "simple_uam/"},
    "util": {"src_dir": "subpackages/util/util/"},
}

for package, data in packages.items():

    src_dir = Path(data['src_dir'])

    for path in sorted(src_dir.rglob("*.py")):

        module_path = path.relative_to(src_dir.parent).with_suffix("")
        doc_path = path.relative_to(src_dir.parent).with_suffix(".md")
        full_doc_path = Path("reference", doc_path)


        parts = tuple(module_path.parts)

        if parts[-1] == "__init__":
            parts = parts[:-1]
            doc_path = doc_path.with_name("index.md")
            full_doc_path = full_doc_path.with_name("index.md")
        elif parts[-1] == "__main__":
            continue

        nav[parts] = doc_path.as_posix()


        with mkdocs_gen_files.open(full_doc_path, "w") as fd:

            ident = ".".join(parts)

            fd.write(f"::: {ident}")

        mkdocs_gen_files.set_edit_path(full_doc_path, path)

# add pages manually:
# nav["package", "module"] = "path/to/file.md"

with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())