"""UTF-8 drop-in replacements for various os.path functions.

Dnuos has always assumed UTF-8 as the file system encoding, but this isn't
always the case, especially on Windows. These functions take UTF-8 strings,
decode them to unicode objects, and pass them to the underlying os.path
functions. Any functions that return paths with unicode objects are
encoded back into UTF-8 strings.

This has the effect that UTF-8 can be used even if the file system uses
a different encoding, due to decoding to unicode beforehand.
"""

import os
import sys

def listdir(path):

    try:
        if isinstance(path, bytes):
            path = path.decode('utf-8')
    except UnicodeError:
        # Try to emulate the behavior of os.listdir(u'...') if the path isn't
        # valid for the FS encoding. There's nothing we can do on Windows as
        # os.listdir uses non-wchar APIs for strs.
        if sys.platform == 'win32':
            raise

        fsenc = sys.getfilesystemencoding().lower()
        paths = []
        for p in os.listdir(path):
            try:
                if isinstance(p, bytes):
                    paths.append(p.decode(fsenc))
                else:
                    paths.append(p)
            except UnicodeError:
                paths.append(p)
        return paths

    paths = []
    for p in os.listdir(path):
        # In Python 3, just return the paths as strings
        paths.append(p)
    return paths


def _wrap(func):

    def wrapper(path, *args, **kw):
        try:
            if isinstance(path, bytes):
                return func(path.decode('utf-8'), *args, **kw)
            else:
                return func(path, *args, **kw)
        except UnicodeError:
            return func(path, *args, **kw)
    return wrapper


exists = _wrap(os.path.exists)
expanduser = _wrap(os.path.expanduser)
getmtime = _wrap(os.path.getmtime)
getsize = _wrap(os.path.getsize)
isdir = _wrap(os.path.isdir)
isfile = _wrap(os.path.isfile)
mkdir = _wrap(os.mkdir)
makedirs = _wrap(os.makedirs)
normpath = _wrap(os.path.normpath)
rename = _wrap(os.rename)
remove = _wrap(os.remove)
rmdir = _wrap(os.rmdir)
open = _wrap(open)
