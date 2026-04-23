"""MCP server — exposes GET-only JustCall tools to the agent.

The agent sees exactly four tools. It has no way to express a DELETE,
PUT, or POST against JustCall because no such tool is registered.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from . import audit, ratelimit
from .client import JustCallClient

mcp = FastMCP("justcall-readonly")
_client = JustCallClient()


@mcp.tool()
def list_calls(
    from_datetime: str | None = None,
    to_datetime: str | None = None,
    agent_id: int | None = None,
    per_page: int = 50,
    page: int = 1,
) -> dict:
    """List JustCall calls in a date range, optionally filtered by agent."""
    args = {
        "from_datetime": from_datetime,
        "to_datetime": to_datetime,
        "agent_id": agent_id,
        "per_page": per_page,
        "page": page,
    }
    with audit.record("list_calls", args):
        ratelimit.acquire()
        return _client.list_calls(**args)


@mcp.tool()
def get_call(call_id: int) -> dict:
    """Fetch metadata for a single call by ID."""
    with audit.record("get_call", {"call_id": call_id}):
        ratelimit.acquire()
        return _client.get_call(call_id)


@mcp.tool()
def get_recording(call_id: int) -> dict:
    """Fetch the recording URL for a call."""
    with audit.record("get_recording", {"call_id": call_id}):
        ratelimit.acquire()
        return _client.get_recording(call_id)


@mcp.tool()
def get_transcript(call_id: int) -> dict:
    """Fetch the transcript for a call."""
    with audit.record("get_transcript", {"call_id": call_id}):
        ratelimit.acquire()
        return _client.get_transcript(call_id)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
