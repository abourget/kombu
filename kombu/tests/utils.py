import __builtin__
import sys
import types

from StringIO import StringIO

from kombu.utils.functional import wraps

try:
    import unittest
    unittest.skip
except AttributeError:
    import unittest2 as unittest


def redirect_stdouts(fun):

    @wraps(fun)
    def _inner(*args, **kwargs):
        sys.stdout = StringIO()
        sys.stderr = StringIO()
        try:
            return fun(*args, **dict(kwargs, stdout=sys.stdout,
                                             stderr=sys.stderr))
        finally:
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__

    return _inner


def module_exists(*modules):

    def _inner(fun):

        @wraps(fun)
        def __inner(*args, **kwargs):
            for module in modules:
                if isinstance(module, basestring):
                    module = types.ModuleType(module)
                sys.modules[module.__name__] = module
                try:
                    return fun(*args, **kwargs)
                finally:
                    sys.modules.pop(module.__name__, None)

        return __inner
    return _inner


# Taken from
# http://bitbucket.org/runeh/snippets/src/tip/missing_modules.py
def mask_modules(*modnames):
    """Ban some modules from being importable inside the context

    For example:

        >>> @missing_modules("sys"):
        >>> def foo():
        ...     try:
        ...         import sys
        ...     except ImportError:
        ...         print "sys not found"
        sys not found

        >>> import sys
        >>> sys.version
        (2, 5, 2, 'final', 0)

    """

    def _inner(fun):

        @wraps(fun)
        def __inner(*args, **kwargs):
            realimport = __builtin__.__import__

            def myimp(name, *args, **kwargs):
                if name in modnames:
                    raise ImportError("No module named %s" % name)
                else:
                    return realimport(name, *args, **kwargs)

            __builtin__.__import__ = myimp
            try:
                return fun(*args, **kwargs)
            finally:
                __builtin__.__import__ = realimport

        return __inner
    return _inner
