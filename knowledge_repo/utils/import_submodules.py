import sys
import importlib
import pkgutil


def import_submodules(package_name):
    """ Import all submodules of a module, recursively

    :param package_name: Package name
    :type package_name: str
    :rtype: list[types.ModuleType]
    """
    package = sys.modules[package_name]
    submodules = []
    for _, name, _ in pkgutil.walk_packages(package.__path__):
        importlib.import_module(package_name + '.' + name)
        submodules.append(name)
    return submodules
