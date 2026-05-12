from __future__ import annotations

import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from .events import Event, TraceWriter, new_session_id
from .gitmeta import git_changed_files, git_commit, git_diff, git_status, is_git_repo


@dataclass(frozen=True)
class RunResult:
    session_id: str
    trace_path: Path
    exit_code: int


def default_trace_dir(cwd: Path) -> Path:
    return cwd / ".agent-rec" / "sessions"


def record_run(command: list[str], cwd: Path, trace_dir: Path | None = None) -> RunResult:
    if not command:
        raise ValueError("command must not be empty")

    cwd = cwd.resolve()
    session_id = new_session_id()
    output_dir = trace_dir or default_trace_dir(cwd)
    trace_path = output_dir / f"{session_id}.jsonl"
    writer = TraceWriter(trace_path)

    in_repo = is_git_repo(cwd)
    before_commit = git_commit(cwd) if in_repo else None
    before_status = git_status(cwd) if in_repo else None

    writer.append(
        Event(
            type="session.started",
            session_id=session_id,
            data={
                "cwd": str(cwd),
                "command": command,
                "pid": os.getpid(),
                "git": {
                    "is_repo": in_repo,
                    "commit": before_commit,
                    "status": before_status,
                },
            },
        )
    )

    start = time.monotonic()
    process = subprocess.Popen(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
    )
    writer.append(
        Event(
            type="process.started",
            session_id=session_id,
            data={"pid": process.pid, "command": command},
        )
    )

    assert process.stdout is not None
    for line in process.stdout:
        print(line, end="")
        writer.append(
            Event(
                type="process.output",
                session_id=session_id,
                data={"stream": "stdout", "text": line},
            )
        )

    exit_code = process.wait()
    duration_ms = int((time.monotonic() - start) * 1000)
    writer.append(
        Event(
            type="process.exited",
            session_id=session_id,
            data={"exit_code": exit_code, "duration_ms": duration_ms},
        )
    )

    after_status = git_status(cwd) if in_repo else None
    after_diff = git_diff(cwd) if in_repo else None
    changed_files = git_changed_files(cwd) if in_repo else []
    writer.append(
        Event(
            type="git.snapshot",
            session_id=session_id,
            data={
                "is_repo": in_repo,
                "commit_before": before_commit,
                "commit_after": git_commit(cwd) if in_repo else None,
                "status_before": before_status,
                "status_after": after_status,
                "changed_files": changed_files,
                "diff": after_diff,
            },
        )
    )
    writer.append(
        Event(
            type="session.finished",
            session_id=session_id,
            data={"exit_code": exit_code, "duration_ms": duration_ms},
        )
    )
    return RunResult(session_id=session_id, trace_path=trace_path, exit_code=exit_code)
