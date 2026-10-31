import importlib
import pkgutil

import journal


def test_every_journal_module_imports():
    prefix = f"{journal.__name__}."
    for module in pkgutil.walk_packages(journal.__path__, prefix):
        importlib.import_module(module.name)
