import ast
import importlib
from importlib.machinery import BuiltinImporter, FrozenImporter, PathFinder
import pkgutil
import re
import shlex
import shutil
import sys
import sysconfig
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


def test_gateway_bridge_imports_with_only_its_archived_python_packages(tmp_path):
    profile = SOURCE.parent / "docs" / "supervisor" / "v1"
    build = (profile / "build-gateway.sh").read_text()
    dockerfile = (profile / "Dockerfile.gateway").read_text()
    archive = build.split(
        'git -C "$RUNTIME_SOURCE" archive --format=tar "$PROFILE_REVISION" --', 1
    )[1].split('> "$BUILD_CONTEXT/runtime.tar"', 1)[0]
    archived = {
        item for line in archive.splitlines()
        if (item := line.strip().removesuffix("\\").strip())
    }
    copies = re.findall(
        r"^COPY (src/\S+) /opt/journal-supervisor/lib/(\S+)$",
        dockerfile,
        re.MULTILINE,
    )
    assert copies and all(source in archived for source, _ in copies), (
        "gateway Python copies come from its archived sources"
    )

    library = tmp_path / "lib"
    for source, target in copies:
        source_path = SOURCE.parent / source
        target_path = library / target
        if source_path.is_dir():
            shutil.copytree(source_path, target_path)
        else:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, target_path)

    package_names = ("journal", "supervisor_bridge")
    previous_modules = {
        name: module for name, module in sys.modules.items()
        if any(name == package or name.startswith(f"{package}.") for package in package_names)
    }
    previous_path = sys.path[:]
    previous_finders = sys.meta_path[:]
    bridge_file = ""
    journal_files = {}
    standard_library = (
        sysconfig.get_path("stdlib"),
        sysconfig.get_config_var("DESTSHARED"),
    )
    try:
        for name in previous_modules:
            del sys.modules[name]
        sys.path[:] = [str(library), *(path for path in standard_library if path)]
        sys.meta_path[:] = [BuiltinImporter, FrozenImporter, PathFinder]
        importlib.invalidate_caches()
        bridge = importlib.import_module("supervisor_bridge.bridge")
        bridge_file = bridge.__file__
        journal_files = {
            name: sys.modules[name].__file__
            for name in (
                "journal.features.supervisor.capability_catalogue",
                "journal.features.supervisor.support.supervisor_operation_commands",
            )
        }
    finally:
        for name in tuple(sys.modules):
            if any(name == package or name.startswith(f"{package}.") for package in package_names):
                del sys.modules[name]
        sys.modules.update(previous_modules)
        sys.path[:] = previous_path
        sys.meta_path[:] = previous_finders
        importlib.invalidate_caches()

    assert Path(bridge_file).is_relative_to(library), "the gateway imports the bridge from its copied library"
    assert all(
        Path(path).is_relative_to(library) for path in journal_files.values()
    ), "shared journal definitions come from the gateway library"
    assert {path.removeprefix("src/") for path in archived if path.startswith("src/journal/")} == {
        "journal/__init__.py",
        "journal/features/__init__.py",
        "journal/features/supervisor/capability_catalogue.py",
        "journal/features/supervisor/support/supervisor_operation_commands.py",
    }, "the gateway ships only the journal package markers and definitions the bridge imports"
