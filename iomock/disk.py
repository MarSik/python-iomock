# This file contains the implementation of virtual StringIO based filesystem
#
# Copyright (C) 2010  Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author(s): Martin Sivak <msivak@redhat.com>
#            Tomas Mlcoch <tmlcoch@redhat.com>

from StringIO import StringIO
import fnmatch
import os.path

class DiskIO(object):
    """Simple object to simplify mocking of file operations in Mock
       based testing"""

    class TestFile(StringIO):
        def __init__(self, store, path, content = ""):
            StringIO.__init__(self, content)
            self._store = store
            self._path = path
            self._ro = False

        def flush(self):
            self._store[self._path] = self.getvalue()

        def close(self):
            self.flush()
            return StringIO.close(self)

        def __del__(self):
            try:
                self.close()
            except (AttributeError, ValueError):
                pass

        def __enter__(self):
            return self

        def __exit__(self, *_):
            self.close()

    class Dir(object):
        pass

    class Link(object):
        def __init__(self, diskio, target):
            self.target = target
            self._diskio = diskio

        @property
        def content(self, stack = {}, source = ""):
            if self in stack:
                raise Exception("Infinite recursion in symlinks")

            target = os.path.join(source, self.target)

            content = self._diskio.get(target, None)
            if hasattr(content, "content"):
                stack[self] = True
                content = content.content(stack = stack, source = target)

            return content
                
    def __init__(self):
        self.umask = 022
        self.uid = 0
        self.gid = 0
        
        self.reset()

    def __getitem__(self, key):
        return self.fs[key]

    def __setitem__(self, key, value):
        self.fs[key] = value
        self.ugo.setdefault(key, 0666 & (~self.umask))
        self.owner.setdefault(key, self.uid)
        self.group.setdefault(key, self.gid)
        
    def reset(self):
        self.fs = {
            "/proc": self.Dir,
            "/proc/cmdline": "linux",
        }
        self.ugo = {}
        self.owner = {}
        self.group = {}
        self.cwd = "/"

    #Emulate file objects
    def open(self, filename, mode = "r"):
        path = os.path.join(self.cwd, filename)
        content = self.fs.get(path, None)

        if hasattr(content, "content"):
            content = content.content(source = path)
        
        if content == self.Dir:
            raise IOError("[Errno 21] Is a directory: '%s'" % (path))
        elif mode.startswith("w"):
            self.fs[path] = ""
            self.ugo.setdefault(path, 0666 & (~self.umask))
            self.owner.setdefault(path, self.uid)
            self.group.setdefault(path, self.gid)
            f = self.TestFile(self.fs, path, self.fs[path])
        elif mode.endswith("a"):
            if not path in self.fs:
                self.fs[path] = ""
                self.ugo[path] = 0666 & (~self.umask)
                self.owner.setdefault(path, self.uid)
                self.group.setdefault(path, self.gid)
            f = self.TestFile(self.fs, path, self.fs[path])
            f.seek(0, os.SEEK_END)
        elif content == None:
            raise IOError("[Errno 2] No such file or directory: '%s'" % (path,))
        elif mode.endswith("+"):
            f = self.TestFile(self.fs, path, content)
            if mode.startswith('r'):
                f.seek(0, os.SEEK_SET)
            else:
                f.seek(0, os.SEEK_END)
        else:
            f = self.TestFile(self.fs, path, content)

        return f

    #Emulate os calls
    def glob_glob(self, pattern):
        return fnmatch.filter(self.fs.keys(), pattern)

    def os_listdir(self, path):
        return [entry[len(path):].lstrip('/') for entry in self.fs.keys()\
                    if entry.startswith(path) and entry != path]

    def os_path_exists(self, path):
        path = os.path.join(self.cwd, path)
        return self.fs.has_key(path)

    def os_path_isdir(self, path):
        if not path.endswith("/"):
            path += "/"
        path += "*"
        return len(fnmatch.filter(self.fs.keys(), path)) > 0

    def os_remove(self, path):
        path = os.path.join(self.cwd, path)
        try:
            del self.fs[path]
        except KeyError:
            raise OSError("[Errno 2] No such file or directory: '%s'" % (path,))

    def os_access(self, path, mode):
        return self.os_path_exists(path)

    def os_chdir(self, path):
        self.cwd = path

    def os_chmod(self, path, mode):
        try:
            old = self.ugo[path]
            self.ugo[path] = mode
        except KeyError:
            raise OSError("[Errno 2] No such file or directory: '%s'" % (path,))
        
    def os_chown(self, path, uid, gid):
        try:
            _old = self.owner[path]
            if uid >= 0:
                self.owner[path] = uid
            if gid >= 0:
                self.group[path] = gid
        except KeyError:
            raise OSError("[Errno 2] No such file or directory: '%s'" % (path,))

    def os_readlink(self, path):
        try:
            path = os.path.join(self.cwd, path)
            link = self.fs[path]
            if not isinstance(link, self.Link):
                raise OSError("[Errno 22] Invalid argument: '%s'" % (path,))
            
            return link.target
        except KeyError:
            raise OSError("[Errno 2] No such file or directory: '%s'" % (path,))

    def os_symlink(self, target, path):
        path = os.path.join(self.cwd, path)
        self.fs[path] = self.Link(diskio = self, target = target)
