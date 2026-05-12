from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]


def test_trace_event_schema_validates_example_trace():
    schema = json.loads((ROOT / "schemas" / "trace-event.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)

    for line in (ROOT / "examples" / "basic-trace.jsonl").read_text(encoding="utf-8").splitlines():
        event = json.loads(line)
        validator.validate(event)


def test_trace_event_schema_rejects_missing_required_fields():
    schema = json.loads((ROOT / "schemas" / "trace-event.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)

    errors = list(validator.iter_errors({"type": "process.output"}))

    assert errors
