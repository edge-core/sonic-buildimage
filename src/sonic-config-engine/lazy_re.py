# monkey patch re.compile to improve import time of some packages

import re

_orig_re_compile = re.compile


def __re_compile(*args, **kwargs):
    class __LazyReCompile(object):
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs
            self.pattern_obj = None

        def __getattr__(self, name):
            if self.pattern_obj is None:
                self.pattern_obj = _orig_re_compile(*self.args, **self.kwargs)
            return getattr(self.pattern_obj, name)
    return __LazyReCompile(*args, **kwargs)

re.compile = __re_compile

