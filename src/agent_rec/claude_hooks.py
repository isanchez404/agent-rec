from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .events import Event, TraceWriter
from .scrub import scrub_value


def parse_claude_hook_payload(payload: dict[str, Any] | str) -> dict[str, Any]:
    if isinstance(payload, str):
        loaded = json.loads(payload)
        if not isinstance(loaded, dict):
            raise ValueError("Claude Code hook payload must be a JSON object")
        return loaded
    return payload


def claude_hook_event_from_payload(payload: dict[str, Any] | str, agent_rec_session_id: str) -> Event:
    raw = parse_claude_hook_payload(payload)
    tool_input = scrub_value(raw.get("tool_input", {})).value
    return Event(
        type="claude_code.hook",
        session_id=agent_rec_session_id,
        data={
            "claude_session_id": raw.get("session_id"),
            "hook_event_name": raw.get("hook_event_name"),
            "tool_name": raw.get("tool_name"),
            "tool_input": tool_input,
            "cwd": raw.get("cwd"),
            "transcript_path": raw.get("transcript_path"),
            "permission_mode": raw.get("permission_mode"),
        },
    )


def write_claude_hook_event(payload: dict[str, Any] | str, trace_path: Path, agent_rec_session_id: str) -> None:
    TraceWriter(trace_path).append(
        claude_hook_event_from_payload(payload, agent_rec_session_id=agent_rec_session_id)
    )
