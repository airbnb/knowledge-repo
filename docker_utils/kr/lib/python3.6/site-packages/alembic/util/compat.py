import io
import sys

if sys.version_info < (2, 7):
    raise NotImplementedError("Python 2.7 or greater is required.")

py27 = sys.version_info >= (2, 7)
py2k = sys.version_info.major < 3
py3k = sys.version_info.major >= 3
py33 = sys.version_info >= (3, 3)
py35 = sys.version_info >= (3, 5)
py36 = sys.version_info >= (3, 6)

if py3k:
    from io import StringIO
else:
    # accepts strings
    from StringIO import StringIO  # noqa

if py3k:
    import builtins as compat_builtins

    string_types = (str,)
    binary_type = bytes
    text_type = str

    def callable(fn):  # noqa
        return hasattr(fn, "__call__")

    def u(s):
        return s

    def ue(s):
        return s

    range = range  # noqa
else:
    import __builtin__ as compat_builtins

    string_types = (basestring,)  # noqa
    binary_type = str
    text_type = unicode  # noqa
    callable = callable  # noqa

    def u(s):
        return unicode(s, "utf-8")  # noqa

    def ue(s):
        return unicode(s, "unicode_escape")  # noqa

    range = xrange  # noqa

if py33:
    import collections.abc as collections_abc
else:
    import collections as collections_abc  # noqa

if py3k:
    import collections

    ArgSpec = collections.namedtuple(
        "ArgSpec", ["args", "varargs", "keywords", "defaults"]
    )

    from inspect import getfullargspec as inspect_getfullargspec

    def inspect_getargspec(func):
        return ArgSpec(*inspect_getfullargspec(func)[0:4])


else:
    from inspect import getargspec as inspect_getargspec  # noqa

if py35:
    from inspect import formatannotation

    def inspect_formatargspec(
        args,
        varargs=None,
        varkw=None,
        defaults=None,
        kwonlyargs=(),
        kwonlydefaults={},
        annotations={},
        formatarg=str,
        formatvarargs=lambda name: "*" + name,
        formatvarkw=lambda name: "**" + name,
        formatvalue=lambda value: "=" + repr(value),
        formatreturns=lambda text: " -> " + text,
        formatannotation=formatannotation,
    ):
        """Copy formatargspec from python 3.7 standard library.

        Python 3 has deprecated formatargspec and requested that Signature
        be used instead, however this requires a full reimplementation
        of formatargspec() in terms of creating Parameter objects and such.
        Instead of introducing all the object-creation overhead and having
        to reinvent from scratch, just copy their compatibility routine.

        """

        def formatargandannotation(arg):
            result = formatarg(arg)
            if arg in annotations:
                result += ": " + formatannotation(annotations[arg])
            return result

        specs = []
        if defaults:
            firstdefault = len(args) - len(defaults)
        for i, arg in enumerate(args):
            spec = formatargandannotation(arg)
            if defaults and i >= firstdefault:
                spec = spec + formatvalue(defaults[i - firstdefault])
            specs.append(spec)
        if varargs is not None:
            specs.append(formatvarargs(formatargandannotation(varargs)))
        else:
            if kwonlyargs:
                specs.append("*")
        if kwonlyargs:
            for kwonlyarg in kwonlyargs:
                spec = formatargandannotation(kwonlyarg)
                if kwonlydefaults and kwonlyarg in kwonlydefaults:
                    spec += formatvalue(kwonlydefaults[kwonlyarg])
                specs.append(spec)
        if varkw is not None:
            specs.append(formatvarkw(formatargandannotation(varkw)))
        result = "(" + ", ".join(specs) + ")"
        if "return" in annotations:
            result += formatreturns(formatannotation(annotations["return"]))
        return result


else:
    from inspect import formatargspec as inspect_formatargspec  # noqa


if py3k:
    from configparser import ConfigParser as SafeConfigParser
    import configparser
else:
    from ConfigParser import SafeConfigParser  # noqa
    import ConfigParser as configparser  # noqa

if py2k:
    from mako.util import parse_encoding

if py35:
    import importlib.util
    import importlib.machinery

    def load_module_py(module_id, path):
        spec = importlib.util.spec_from_file_location(module_id, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def load_module_pyc(module_id, path):
        spec = importlib.util.spec_from_file_location(module_id, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


elif py3k:
    import importlib.machinery

    def load_module_py(module_id, path):
        module = importlib.machinery.SourceFileLoader(
            module_id, path
        ).load_module(module_id)
        del sys.modules[module_id]
        return module

    def load_module_pyc(module_id, path):
        module = importlib.machinery.SourcelessFileLoader(
            module_id, path
        ).load_module(module_id)
        del sys.modules[module_id]
        return module


if py3k:

    def get_bytecode_suffixes():
        try:
            return importlib.machinery.BYTECODE_SUFFIXES
        except AttributeError:
            return importlib.machinery.DEBUG_BYTECODE_SUFFIXES

    def get_current_bytecode_suffixes():
        if py35:
            suffixes = importlib.machinery.BYTECODE_SUFFIXES
        else:
            if sys.flags.optimize:
                suffixes = importlib.machinery.OPTIMIZED_BYTECODE_SUFFIXES
            else:
                suffixes = importlib.machinery.BYTECODE_SUFFIXES

        return suffixes

    def has_pep3147():
        # http://www.python.org/dev/peps/pep-3147/#detecting-pep-3147-availability

        import imp

        return hasattr(imp, "get_tag")


else:
    import imp

    def load_module_py(module_id, path):  # noqa
        with open(path, "rb") as fp:
            mod = imp.load_source(module_id, path, fp)
            if py2k:
                source_encoding = parse_encoding(fp)
                if source_encoding:
                    mod._alembic_source_encoding = source_encoding
            del sys.modules[module_id]
            return mod

    def load_module_pyc(module_id, path):  # noqa
        with open(path, "rb") as fp:
            mod = imp.load_compiled(module_id, path, fp)
            # no source encoding here
            del sys.modules[module_id]
            return mod

    def get_current_bytecode_suffixes():
        if sys.flags.optimize:
            return [".pyo"]  # e.g. .pyo
        else:
            return [".pyc"]  # e.g. .pyc

    def has_pep3147():
        return False


try:
    exec_ = getattr(compat_builtins, "exec")
except AttributeError:
    # Python 2
    def exec_(func_text, globals_, lcl):
        exec("exec func_text in globals_, lcl")


################################################
# cross-compatible metaclass implementation
# Copyright (c) 2010-2012 Benjamin Peterson


def with_metaclass(meta, base=object):
    """Create a base class with a metaclass."""
    return meta("%sBase" % meta.__name__, (base,), {})


################################################

if py3k:

    def reraise(tp, value, tb=None, cause=None):
        if cause is not None:
            value.__cause__ = cause
        if value.__traceback__ is not tb:
            raise value.with_traceback(tb)
        raise value

    def raise_from_cause(exception, exc_info=None):
        if exc_info is None:
            exc_info = sys.exc_info()
        exc_type, exc_value, exc_tb = exc_info
        reraise(type(exception), exception, tb=exc_tb, cause=exc_value)


else:
    exec(
        "def reraise(tp, value, tb=None, cause=None):\n"
        "    raise tp, value, tb\n"
    )

    def raise_from_cause(exception, exc_info=None):
        # not as nice as that of Py3K, but at least preserves
        # the code line where the issue occurred
        if exc_info is None:
            exc_info = sys.exc_info()
        exc_type, exc_value, exc_tb = exc_info
        reraise(type(exception), exception, tb=exc_tb)


# produce a wrapper that allows encoded text to stream
# into a given buffer, but doesn't close it.
# not sure of a more idiomatic approach to this.
class EncodedIO(io.TextIOWrapper):
    def close(self):
        pass


if py2k:
    # in Py2K, the io.* package is awkward because it does not
    # easily wrap the file type (e.g. sys.stdout) and I can't
    # figure out at all how to wrap StringIO.StringIO (used by nosetests)
    # and also might be user specified too.  So create a full
    # adapter.

    class ActLikePy3kIO(object):

        """Produce an object capable of wrapping either
        sys.stdout (e.g. file) *or* StringIO.StringIO().

        """

        def _false(self):
            return False

        def _true(self):
            return True

        readable = seekable = _false
        writable = _true
        closed = False

        def __init__(self, file_):
            self.file_ = file_

        def write(self, text):
            return self.file_.write(text)

        def flush(self):
            return self.file_.flush()

    class EncodedIO(EncodedIO):
        def __init__(self, file_, encoding):
            super(EncodedIO, self).__init__(
                ActLikePy3kIO(file_), encoding=encoding
            )
