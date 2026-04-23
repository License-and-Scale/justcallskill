"""JustCall read-only MCP skill.

Exposes only GET operations against the JustCall API. The real API key
lives inside this package and is never visible to the agent. Destructive
JustCall endpoints (DELETE, PUT, POST) are not exposed as tools and
cannot be reached from the agent side.
"""

from .client import JustCallClient
from .server import main

__all__ = ["JustCallClient", "main"]
__version__ = "0.1.0"
