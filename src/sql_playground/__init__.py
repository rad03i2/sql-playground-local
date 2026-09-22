"""SQL Playground Local public package."""

from .core import Playground, PlaygroundError, QueryResult

__version__ = "1.0.0"
__author__ = "Radwan Abdulhadi Ahmed / @rad03i2"

__all__ = ["Playground", "PlaygroundError", "QueryResult", "__version__"]
