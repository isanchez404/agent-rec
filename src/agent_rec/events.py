from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


SCHEMA_VERSION = "agent-rec.trace.v0"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class Event:
    type: str
    session_id: str
    timestamp: str = field(default_factory=utc_now)
    data: dict[str, Any] = field(default_factory=dict)
    schema: str = SCHEMA_VERSION

    def to_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True, ensure_ascii=False)

    @classmethod
    def from_json(cls, line: str) -> "Event":
        raw = json.loads(line)
        return cls(
            type=raw["type"],
            session_id=raw["session_id"],
            timestamp=raw["timestamp"],
            data=raw.get("data", {}),
            schema=raw.get("schema", SCHEMA_VERSION),
        )


class TraceWriter:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: Event) -> None:
        with self.path.open("a", encoding="utf-8") as f:
            f.write(event.to_json() + "\n")


def new_session_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8]


def read_trace(path: Path) -> list[Event]:
    events: list[Event] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if stripped:
                events.append(Event.from_json(stripped))
    return events
