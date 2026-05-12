from __future__ import annotations

import tarfile
from pathlib import Path

from .events import read_trace
from .report import write_report


def create_bundle(trace_path: Path, output_path: Path) -> None:
    events = read_trace(trace_path)
    bundle_root = output_path.with_suffix("")
    staging = output_path.parent / f".{bundle_root.name}.staging"
    staging.mkdir(parents=True, exist_ok=True)
    try:
        trace_copy = staging / "trace.jsonl"
        report_copy = staging / "report.html"
        readme = staging / "README.md"
        trace_copy.write_text(trace_path.read_text(encoding="utf-8"), encoding="utf-8")
        write_report(trace_path, report_copy)
        session_id = events[0].session_id if events else "unknown"
        readme.write_text(
            f"# agent-rec bundle\n\nSession: `{session_id}`\n\nContents:\n\n- `trace.jsonl`: portable event trace\n- `report.html`: static timeline report\n\n",
            encoding="utf-8",
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with tarfile.open(output_path, "w:gz") as tar:
            for path in [readme, trace_copy, report_copy]:
                tar.add(path, arcname=path.name)
    finally:
        for child in staging.glob("*"):
            child.unlink()
        staging.rmdir()
