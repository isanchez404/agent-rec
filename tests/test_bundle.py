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
