# Mock modules that simulate IO operations over real filesystem
#
# Copyright (C) 2012  Red Hat, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see
# <http://www.gnu.org/licenses/>.
#
# Red Hat Author(s): Martin Sivak <msivak@redhat.com>
#

__all__ = ["prepare_io", "inject_io"]

import os
import glob
from di import inject
from .disk import DiskIO
from functools import wraps

class DummyGlob(object):
    def __init__(self, diskio):
        self.__disk = diskio

    def __getattr__(self, name):
        return getattr(glob, name)

    @wraps(glob.glob)
    def glob(self, name):
        return self.__disk.glob_glob(name)

class DummyOSPath(object):
    def __init__(self, diskio):
        self.__disk = diskio

    def __getattr__(self, name):
        return getattr(os.path, name)

    @wraps(os.path.exists)
    def exists(self, name):
        return self.__disk.os_path_exists(name)

    @wraps(os.path.isdir)
    def isdir(self, name):
        return self.__disk.os_path_isdir(name)
    
class DummyOS(object):
    @inject(DummyOSPath)
    def __init__(self, diskio):
        self.__disk = diskio
        self.path = DummyOSPath(diskio)

    def __getattr__(self, name):
        return getattr(os, name)

    @wraps(os.access)
    def access(self, name, mode):
        return self.__disk.os_access(name, mode)

    @wraps(os.remove)
    def remove(self, name):
        return self.__disk.os_remove(name)

    @wraps(os.listdir)
    def listdir(self, name):
        return self.__disk.os_listdir(name)

    @wraps(os.chdir)
    def chdir(self, path):
        return self.__disk.os_chdir(path)

    @wraps(os.chmod)
    def chmod(self, path, mode):
        return self.__disk.os_chmod(path, mode)

    @wraps(os.chown)
    def chown(self, path, uid, gid):
        return self.__disk.os_chown(path, uid, gid)

    @wraps(os.readlink)
    def readlink(self, path):
        return self.__disk.os_readlink(path)

    @wraps(os.symlink)
    def symlink(self, target, path):
        return self.__disk.os_symlink(target, path)

    
@inject(DiskIO, DummyOS, DummyGlob)
def prepare_io():
    """This method creates a filesystem object and
       returns a tuple (fsobject, object_dict).

      fsobject is the virtual filesystem and object_dict
      is a dictionary which can be used to remap standard
      io modules and methods to work with it.
    """
    diskio = DiskIO()
    modules  = {
        "os": DummyOS(diskio),
        "glob": DummyGlob(diskio),
        "open": diskio.open,
        "file": diskio.open
        }
    
    return diskio, modules

def inject_io(di_registry):
    """This method is a helper that plays nicely with unittests and
       the python-di package. It creates new virtual filesystem,
       registers it's method using the dependency injection
       and returns the filesystem object back for the test to modify
       and query.
    """
    diskio, modules = prepare_io()
    di_registry.register(**modules)
    return diskio
