from __future__ import annotations

import sys

from agent_rec.events import read_trace
from agent_rec.recorder import record_run


def test_record_run_captures_output_and_exit_code(tmp_path):
    result = record_run(
        [sys.executable, "-c", "print('hello from agent')"],
        cwd=tmp_path,
        trace_dir=tmp_path / "sessions",
    )

    assert result.exit_code == 0
    assert result.trace_path.exists()
    events = read_trace(result.trace_path)
    assert [event.type for event in events] == [
        "session.started",
        "process.started",
        "process.output",
        "process.exited",
        "git.snapshot",
        "session.finished",
    ]
    assert events[2].data["text"] == "hello from agent\n"
    assert events[-1].data["exit_code"] == 0


def test_record_run_captures_nonzero_exit(tmp_path):
    result = record_run(
        [sys.executable, "-c", "import sys; sys.exit(7)"],
        cwd=tmp_path,
        trace_dir=tmp_path / "sessions",
    )

    assert result.exit_code == 7
    events = read_trace(result.trace_path)
    assert events[-1].data["exit_code"] == 7


def test_record_run_can_allocate_pty_for_interactive_clis(tmp_path):
    result = record_run(
        [sys.executable, "-c", "import sys; print('isatty=' + str(sys.stdout.isatty()))"],
        cwd=tmp_path,
        trace_dir=tmp_path / "sessions",
        use_pty=True,
    )

    assert result.exit_code == 0
    events = read_trace(result.trace_path)
    started = next(event for event in events if event.type == "process.started")
    output = "".join(event.data["text"] for event in events if event.type == "process.output")
    assert started.data["pty"] is True
    assert "isatty=True" in output
