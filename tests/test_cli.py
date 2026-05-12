from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from agent_rec.cli import app
from agent_rec.events import Event


runner = CliRunner()


def test_inspect_command_prints_summary(tmp_path):
    trace = tmp_path / "trace.jsonl"
    trace.write_text(Event(type="session.finished", session_id="s1", data={"exit_code": 0}).to_json() + "\n")

    result = runner.invoke(app, ["inspect", str(trace)])

    assert result.exit_code == 0
    assert "session_id" in result.output
    assert "s1" in result.output


def test_report_command_writes_html(tmp_path):
    trace = tmp_path / "trace.jsonl"
    out = tmp_path / "report.html"
    trace.write_text(Event(type="session.finished", session_id="s1", data={"exit_code": 0}).to_json() + "\n")

    result = runner.invoke(app, ["report", str(trace), "--out", str(out)])

    assert result.exit_code == 0
    assert out.exists()


def test_run_command_records_process(tmp_path):
    trace_dir = tmp_path / "sessions"

    result = runner.invoke(
        app,
        ["run", "--cwd", str(tmp_path), "--trace-dir", str(trace_dir), "--", "python", "-c", "print('ok')"],
    )

    assert result.exit_code == 0
    assert "ok" in result.output
    assert len(list(Path(trace_dir).glob("*.jsonl"))) == 1
