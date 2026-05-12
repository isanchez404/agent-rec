from __future__ import annotations

import json

from agent_rec.claude_hooks import claude_hook_event_from_payload, write_claude_hook_event
from agent_rec.events import read_trace


def test_claude_hook_event_normalizes_tool_payload():
    payload = {
        "session_id": "claude-session-1",
        "transcript_path": "/tmp/transcript.jsonl",
        "cwd": "/repo",
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": "pytest -q"},
        "permission_mode": "default",
    }

    event = claude_hook_event_from_payload(payload, agent_rec_session_id="agent-session-1")

    assert event.type == "claude_code.hook"
    assert event.session_id == "agent-session-1"
    assert event.data["claude_session_id"] == "claude-session-1"
    assert event.data["hook_event_name"] == "PreToolUse"
    assert event.data["tool_name"] == "Bash"
    assert event.data["tool_input"] == {"command": "pytest -q"}


def test_write_claude_hook_event_appends_jsonl(tmp_path):
    payload = {"session_id": "claude-session-1", "hook_event_name": "PostToolUse", "tool_name": "Edit"}
    trace = tmp_path / "trace.jsonl"

    write_claude_hook_event(payload, trace, agent_rec_session_id="agent-session-1")

    events = read_trace(trace)
    assert len(events) == 1
    assert events[0].type == "claude_code.hook"
    assert events[0].data["tool_name"] == "Edit"


def test_write_claude_hook_event_accepts_json_from_stdin_shape(tmp_path):
    payload_text = json.dumps({"session_id": "claude-session-2", "hook_event_name": "Stop"})
    trace = tmp_path / "trace.jsonl"

    write_claude_hook_event(payload_text, trace, agent_rec_session_id="agent-session-2")

    events = read_trace(trace)
    assert events[0].data["hook_event_name"] == "Stop"
