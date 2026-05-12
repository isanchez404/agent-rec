from __future__ import annotations

import tarfile

from agent_rec.bundle import create_bundle
from agent_rec.events import Event


def test_create_bundle_contains_trace_report_and_readme(tmp_path):
    trace = tmp_path / "trace.jsonl"
    trace.write_text(Event(type="session.finished", session_id="s1", data={"exit_code": 0}).to_json() + "\n")
    out = tmp_path / "bundle.tar.gz"

    create_bundle(trace, out)

    assert out.exists()
    with tarfile.open(out, "r:gz") as tar:
        names = set(tar.getnames())
    assert names == {"README.md", "trace.jsonl", "report.html"}


def test_create_bundle_scrubs_trace_and_report_by_default(tmp_path):
    trace = tmp_path / "trace.jsonl"
    trace.write_text(
        Event(type="process.output", session_id="s1", data={"text": "OPENAI_API_KEY=sk-abc1234567890abcdef\n"}).to_json() + "\n",
        encoding="utf-8",
    )
    out = tmp_path / "bundle.tar.gz"

    create_bundle(trace, out)

    with tarfile.open(out, "r:gz") as tar:
        trace_text = tar.extractfile("trace.jsonl").read().decode("utf-8")  # type: ignore[union-attr]
        report_text = tar.extractfile("report.html").read().decode("utf-8")  # type: ignore[union-attr]
    assert "sk-abc" not in trace_text
    assert "sk-abc" not in report_text
    assert "[REDACTED:openai_key]" in trace_text
    assert "[REDACTED:openai_key]" in report_text
