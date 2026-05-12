from __future__ import annotations

import html
from pathlib import Path

from .events import Event, read_trace


CSS = """
body { font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, sans-serif; margin: 0; background: #0b1020; color: #e5e7eb; }
header { padding: 24px 32px; background: #111827; border-bottom: 1px solid #263044; }
main { display: grid; grid-template-columns: 360px 1fr; min-height: calc(100vh - 90px); }
.timeline { border-right: 1px solid #263044; padding: 16px; overflow: auto; }
.details { padding: 16px; overflow: auto; }
.event { padding: 10px 12px; border: 1px solid #263044; border-radius: 10px; margin-bottom: 10px; background: #111827; }
.event strong { color: #93c5fd; }
pre { white-space: pre-wrap; word-wrap: break-word; background: #020617; color: #d1d5db; padding: 12px; border-radius: 10px; border: 1px solid #263044; }
.badge { display: inline-block; border: 1px solid #475569; border-radius: 999px; padding: 2px 8px; font-size: 12px; color: #cbd5e1; }
.fail { color: #fca5a5; }
.ok { color: #86efac; }
"""


def summarize(events: list[Event]) -> dict[str, object]:
    session = events[0].session_id if events else "unknown"
    exit_events = [event for event in events if event.type == "session.finished"]
    exit_code = exit_events[-1].data.get("exit_code") if exit_events else None
    output_lines = sum(1 for event in events if event.type == "process.output")
    git_events = [event for event in events if event.type == "git.snapshot"]
    changed_files = git_events[-1].data.get("changed_files", []) if git_events else []
    return {
        "session_id": session,
        "exit_code": exit_code,
        "event_count": len(events),
        "output_lines": output_lines,
        "changed_files": changed_files,
    }


def event_card(event: Event) -> str:
    title = html.escape(event.type)
    timestamp = html.escape(event.timestamp)
    data = html.escape(str(event.data))
    return f'<div class="event"><strong>{title}</strong><br><span class="badge">{timestamp}</span><pre>{data}</pre></div>'


def render_report(events: list[Event]) -> str:
    summary = summarize(events)
    exit_code = summary["exit_code"]
    status_class = "ok" if exit_code == 0 else "fail"
    changed_files = summary["changed_files"] or []
    changed_html = "".join(f"<li>{html.escape(str(path))}</li>" for path in changed_files)
    cards = "\n".join(event_card(event) for event in events)
    output_text = "".join(str(event.data.get("text", "")) for event in events if event.type == "process.output")
    output_html = html.escape(output_text)

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>agent-rec report {html.escape(str(summary['session_id']))}</title>
<style>{CSS}</style>
</head>
<body>
<header>
  <h1>agent-rec report</h1>
  <p>Session <span class="badge">{html.escape(str(summary['session_id']))}</span>
  Exit <strong class="{status_class}">{html.escape(str(exit_code))}</strong>
  Events <span class="badge">{summary['event_count']}</span></p>
</header>
<main>
  <section class="timeline">
    <h2>Timeline</h2>
    {cards}
  </section>
  <section class="details">
    <h2>Changed files</h2>
    <ul>{changed_html}</ul>
    <h2>Process output</h2>
    <pre>{output_html}</pre>
  </section>
</main>
</body>
</html>
"""


def write_report(trace_path: Path, output_path: Path) -> None:
    events = read_trace(trace_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_report(events), encoding="utf-8")
