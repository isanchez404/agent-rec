from __future__ import annotations

import subprocess
from pathlib import Path


def is_git_repo(cwd: Path) -> bool:
    result = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=cwd,
        text=True,
        capture_output=True,
    )
    return result.returncode == 0 and result.stdout.strip() == "true"


def git_commit(cwd: Path) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=cwd,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def git_status(cwd: Path) -> str | None:
    result = subprocess.run(
        ["git", "status", "--short"],
        cwd=cwd,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout


def git_diff(cwd: Path) -> str | None:
    result = subprocess.run(
        ["git", "diff", "--binary"],
        cwd=cwd,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout


def git_changed_files(cwd: Path) -> list[str]:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=cwd,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        return []
    files: list[str] = []
    for line in result.stdout.splitlines():
        if not line:
            continue
        files.append(line[3:] if len(line) > 3 else line)
    return files
