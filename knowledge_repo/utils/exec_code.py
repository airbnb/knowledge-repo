import sys
import imp
import time


def get_module_for_source(source, module_name, register_globally=True):
    module_name = module_name + '_' + str(time.time()).replace('.', '')
    module = imp.new_module(module_name)
    exec(source, module.__dict__)
    if register_globally:
        sys.modules[module_name] = module
    return module
