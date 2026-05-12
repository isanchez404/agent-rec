from __future__ import annotations

from agent_rec.events import Event
from agent_rec.report import render_report, summarize, write_report


def test_summarize_counts_outputs_and_changed_files():
    events = [
        Event(type="session.started", session_id="s1"),
        Event(type="process.output", session_id="s1", data={"text": "hi\n"}),
        Event(type="git.snapshot", session_id="s1", data={"changed_files": ["a.py"]}),
        Event(type="session.finished", session_id="s1", data={"exit_code": 0}),
    ]

    summary = summarize(events)

    assert summary["session_id"] == "s1"
    assert summary["exit_code"] == 0
    assert summary["output_lines"] == 1
    assert summary["changed_files"] == ["a.py"]


def test_render_report_escapes_output():
    events = [Event(type="process.output", session_id="s1", data={"text": "<secret>\n"})]

    html = render_report(events)

    assert "&lt;secret&gt;" in html
    assert "<secret>" not in html


def test_render_report_has_dedicated_diff_pane_and_scrubs_secrets():
    events = [
        Event(type="process.output", session_id="s1", data={"text": "OPENAI_API_KEY=sk-abc1234567890abcdef\n"}),
        Event(
            type="git.snapshot",
            session_id="s1",
            data={
                "changed_files": ["a.py"],
                "diff": "diff --git a/a.py b/a.py\n+print('hello')\n",
            },
        ),
        Event(type="session.finished", session_id="s1", data={"exit_code": 0}),
    ]

    html = render_report(events)

    assert "Git diff" in html
    assert "diff --git" in html
    assert "print(&#x27;hello&#x27;)" in html
    assert "sk-abc" not in html
    assert "[REDACTED:openai_key]" in html


def test_write_report_creates_file(tmp_path):
    trace = tmp_path / "trace.jsonl"
    trace.write_text(Event(type="session.finished", session_id="s1", data={"exit_code": 0}).to_json() + "\n")
    out = tmp_path / "report.html"

    write_report(trace, out)

    assert out.exists()
    assert "agent-rec report" in out.read_text(encoding="utf-8")
