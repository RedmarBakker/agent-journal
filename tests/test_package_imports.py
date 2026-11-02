import ast
import importlib
import pkgutil
import re
import shlex
from pathlib import Path

import journal


SOURCE = Path(__file__).resolve().parents[1] / "src"


def test_every_journal_module_imports():
    prefix = f"{journal.__name__}."
    for module in pkgutil.walk_packages(journal.__path__, prefix):
        importlib.import_module(module.name)


def test_every_shipped_package_imports_only_packages_install_ships():
    install_script = (SOURCE.parent / "install.sh").read_text()
    match = re.search(r"for name in ([^;]+); do", install_script)
    assert match is not None, "install.sh names the source parts it copies"
    shipped = {
        name for name in shlex.split(match.group(1))
        if (SOURCE / name).is_dir()
    }
    local_packages = {
        package.name for package in SOURCE.iterdir()
        if package.is_dir() and (package / "__init__.py").is_file()
    }
    unshipped = local_packages - shipped
    imports = []
    for package in sorted(shipped):
        for path in (SOURCE / package).rglob("*.py"):
            for node in ast.walk(ast.parse(path.read_text(), filename=str(path))):
                names = (
                    [alias.name for alias in node.names]
                    if isinstance(node, ast.Import)
                    else [node.module] if isinstance(node, ast.ImportFrom) and node.module
                    else []
                )
                imports.extend(
                    f"{path.relative_to(SOURCE)} imports unshipped package {name}"
                    for name in names
                    if name.split(".", 1)[0] in unshipped
                )
    assert not imports, "\n".join(imports)
