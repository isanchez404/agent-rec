from __future__ import annotations

from agent_rec.events import Event, read_trace


def test_event_round_trips_json(tmp_path):
    event = Event(type="process.output", session_id="s1", data={"text": "hello"})
    path = tmp_path / "trace.jsonl"
    path.write_text(event.to_json() + "\n", encoding="utf-8")

    loaded = read_trace(path)

    assert len(loaded) == 1
    assert loaded[0].type == "process.output"
    assert loaded[0].session_id == "s1"
    assert loaded[0].data == {"text": "hello"}
