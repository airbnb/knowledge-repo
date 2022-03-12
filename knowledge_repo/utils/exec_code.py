import importlib
import sys
import time


def get_module_for_source(source, module_name, register_globally=True):
    module_name = module_name + '_' + str(time.time()).replace('.', '')
    spec = importlib.util.find_spec(module_name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if register_globally:
        sys.modules[module_name] = module
    return module
