"""Invariant tests.

These tests exist to make the GET-only guarantee load-bearing. If anyone
later adds a POST / PUT / DELETE to client.py, these tests fail and the
security property of the skill is restored by rejecting the change.
"""

from __future__ import annotations

import inspect
import re

from justcall_readonly import client


def test_no_non_get_method_literals_in_client():
    """The string 'POST', 'PUT', 'DELETE', 'PATCH' must never appear in client.py."""
    source = inspect.getsource(client)
    forbidden = ["POST", "PUT", "DELETE", "PATCH"]
    for verb in forbidden:
        assert re.search(rf'["\']{verb}["\']', source) is None, (
            f"{verb} appeared as a string literal in client.py — "
            "this skill must remain GET-only"
        )


def test_every_public_method_issues_get(monkeypatch):
    """Every public JustCallClient method must route through _get."""
    calls: list[str] = []

    def fake_request(method, url, **_):
        calls.append(method)
        class R:
            def raise_for_status(self): pass
            def json(self): return {}
        return R()

    monkeypatch.setattr(client.httpx, "request", fake_request)
    c = client.JustCallClient(api_key="x", api_secret="y")

    c.list_calls()
    c.get_call(1)
    c.get_recording(1)
    c.get_transcript(1)

    assert calls, "no requests were made"
    assert all(m == "GET" for m in calls), f"non-GET request issued: {calls}"
