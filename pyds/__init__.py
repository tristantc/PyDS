"""Convenience import layer so users can do `from pyds import PyDS`.

The core implementation currently lives in the top-level `PyDS.py` module.
This package wrapper re-exports the class and exposes a version string.
"""

from ._version import __version__  # noqa: F401

# Import the class from the single-file module at repository root.
# Using importlib to avoid relative import beyond top-level package issues.
import importlib as _importlib

_core_mod = _importlib.import_module("PyDS")
PyDS = getattr(_core_mod, "PyDS")

__all__ = ["PyDS", "__version__"]
