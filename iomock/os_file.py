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

@inject(DiskIO, DummyOS, DummyGlob)
def takeover():
    diskio = DiskIO()
    modules  = {
        "os": DummyOS(diskio),
        "glob": DummyGlob(diskio),
        "open": diskio.open,
        "file": diskio.open
        }
    
    return diskio, modules
