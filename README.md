# justcall-readonly

A **GET-only** [MCP](https://modelcontextprotocol.io) skill for [JustCall](https://justcall.io).
Drop-in companion skill for the
[L-S-SALES-INTELLIGENCE-TEMPLATE](https://github.com/License-and-Scale/L-S-SALES-INTELLIGENCE-TEMPLATE)
archetype, but usable by any MCP-capable agent.

## Why this exists

JustCall API keys are **fully scoped** — the same key that lists calls can
delete them. For an LLM agent that ingests call transcripts (an adversarial
input surface via prompt injection), unrestricted write access is unacceptable.

This skill restricts access at the **tool-vocabulary** level:

- The agent's tool list contains only four GET operations.
- Destructive verbs (DELETE / PUT / POST) are not exposed and cannot be called —
  the function signatures do not exist in the MCP schema.
- The real `JUSTCALL_API_KEY` / `JUSTCALL_API_SECRET` live inside the skill
  process. The agent never sees them.
- An invariant test enforces that `client.py` contains no non-GET method
  literals. If a future change adds one, CI fails.

## Exposed tools

| Tool | JustCall endpoint |
|------|-------------------|
| `list_calls(from_datetime, to_datetime, agent_id, per_page, page)` | `GET /v2/calls` |
| `get_call(call_id)` | `GET /v2/calls/{id}` |
| `get_recording(call_id)` | `GET /v2/calls/{id}/recording` |
| `get_transcript(call_id)` | `GET /v2/calls/{id}/transcript` |

## Install

```bash
pip install -e .
```

Or add to your OpenClaw profile:

```bash
openclaw skills install github:License-and-Scale/justcallskill --profile my-agent
```

## Configure

Set in your `.env` (or OpenClaw profile env):

```
JUSTCALL_API_KEY=...
JUSTCALL_API_SECRET=...
```

Optional:

```
JUSTCALL_BASE_URL=https://api.justcall.io/v2         # override for sandboxes
JUSTCALL_AUDIT_DB=~/.justcall-audit.db               # SQLite path
JUSTCALL_RATE_LIMIT_PER_MIN=60                       # quota guard
```

## Run

```bash
python -m justcall_readonly.server
```

## Defense-in-depth

Layers baked in:

1. **Tool vocabulary** — the only hard wall. Non-GET verbs do not exist in the
   MCP schema the agent sees.
2. **Hardcoded HTTP method** — every request in `client.py` passes
   `method="GET"`. No caller parameter can change it.
3. **Hidden credentials** — API key/secret are read from env at skill startup
   and never appear in tool arguments or responses.
4. **Rate limit** — 60 req/min default, protects against runaway loops.
5. **Audit log** — every invocation written to SQLite with timestamp, args,
   outcome. Review with any SQLite client.
6. **Invariant test** — `tests/test_client.py` fails if any non-GET method
   literal is introduced.

## Test

```bash
pip install -e ".[dev]"
pytest
```

## License

MIT.
