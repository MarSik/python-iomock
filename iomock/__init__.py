"""This module provides methods which allow testing of IO operations
without touching the real hardware. It is intended to be used in
unittesting environments."""

__all__ = ["prepare_io", "inject_io"]

from .os_file import *
