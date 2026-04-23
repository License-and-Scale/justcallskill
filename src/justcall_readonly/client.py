"""JustCall HTTP client — GET only.

Every method in this module hardcodes method="GET". There is no parameter
the caller can supply to change the HTTP verb. This is the primary safety
boundary: even if a caller wanted to DELETE a call, there is no code path
that would issue a non-GET request.
"""

from __future__ import annotations

import os
from typing import Any
from urllib.parse import urlencode

import httpx

BASE_URL = os.environ.get("JUSTCALL_BASE_URL", "https://api.justcall.io/v2")
DEFAULT_TIMEOUT = 30.0


class JustCallClient:
    def __init__(
        self,
        api_key: str | None = None,
        api_secret: str | None = None,
        base_url: str = BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self.api_key = api_key or os.environ["JUSTCALL_API_KEY"]
        self.api_secret = api_secret or os.environ["JUSTCALL_API_SECRET"]
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        if params:
            url = f"{url}?{urlencode({k: v for k, v in params.items() if v is not None})}"
        resp = httpx.request(
            method="GET",
            url=url,
            auth=(self.api_key, self.api_secret),
            headers={"Accept": "application/json"},
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()

    def list_calls(
        self,
        from_datetime: str | None = None,
        to_datetime: str | None = None,
        agent_id: int | None = None,
        per_page: int = 50,
        page: int = 1,
    ) -> dict[str, Any]:
        return self._get(
            "/calls",
            {
                "from_datetime": from_datetime,
                "to_datetime": to_datetime,
                "agent_id": agent_id,
                "per_page": per_page,
                "page": page,
            },
        )

    def get_call(self, call_id: int) -> dict[str, Any]:
        return self._get(f"/calls/{call_id}")

    def get_recording(self, call_id: int) -> dict[str, Any]:
        return self._get(f"/calls/{call_id}/recording")

    def get_transcript(self, call_id: int) -> dict[str, Any]:
        return self._get(f"/calls/{call_id}/transcript")
