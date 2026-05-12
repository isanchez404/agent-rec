from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from typing import Any


SECRET_KEY_RE = re.compile(r"(?:api[_-]?key|token|secret|password|authorization)", re.IGNORECASE)
PATTERNS: list[tuple[str, re.Pattern[str], str]] = [
    ("openai_key", re.compile(r"sk-[A-Za-z0-9_-]{16,}"), "[REDACTED:openai_key]"),
    ("anthropic_key", re.compile(r"sk-ant-[A-Za-z0-9_-]{16,}"), "[REDACTED:anthropic_key]"),
    ("github_token", re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"), "[REDACTED:github_token]"),
    ("bearer_token", re.compile(r"Bearer\s+[A-Za-z0-9._~+/-]{20,}", re.IGNORECASE), "Bearer [REDACTED:bearer_token]"),
    ("aws_access_key", re.compile(r"AKIA[0-9A-Z]{16}"), "[REDACTED:aws_access_key]"),
]


@dataclass(frozen=True)
class ScrubResult:
    text: str
    redactions: dict[str, int]


@dataclass(frozen=True)
class ScrubValueResult:
    value: Any
    redactions: dict[str, int]


def _merge(counter: Counter[str], redactions: dict[str, int]) -> None:
    for key, count in redactions.items():
        counter[key] += count


def scrub_text(text: str) -> ScrubResult:
    redactions: Counter[str] = Counter()
    scrubbed = text
    for name, pattern, replacement in PATTERNS:
        scrubbed, count = pattern.subn(replacement, scrubbed)
        if count:
            redactions[name] += count
    return ScrubResult(text=scrubbed, redactions=dict(redactions))


def scrub_value(value: Any, key_hint: str | None = None) -> ScrubValueResult:
    redactions: Counter[str] = Counter()
    if isinstance(value, dict):
        scrubbed_dict = {}
        for key, child in value.items():
            child_result = scrub_value(child, key_hint=str(key))
            scrubbed_dict[key] = child_result.value
            _merge(redactions, child_result.redactions)
        return ScrubValueResult(value=scrubbed_dict, redactions=dict(redactions))
    if isinstance(value, list):
        scrubbed_list = []
        for child in value:
            child_result = scrub_value(child, key_hint=key_hint)
            scrubbed_list.append(child_result.value)
            _merge(redactions, child_result.redactions)
        return ScrubValueResult(value=scrubbed_list, redactions=dict(redactions))
    if isinstance(value, tuple):
        scrubbed_items = []
        for child in value:
            child_result = scrub_value(child, key_hint=key_hint)
            scrubbed_items.append(child_result.value)
            _merge(redactions, child_result.redactions)
        return ScrubValueResult(value=tuple(scrubbed_items), redactions=dict(redactions))
    if isinstance(value, str):
        if key_hint and SECRET_KEY_RE.search(key_hint):
            redactions["secret_value"] += 1
            return ScrubValueResult(value="[REDACTED:secret_value]", redactions=dict(redactions))
        scrubbed = scrub_text(value)
        return ScrubValueResult(value=scrubbed.text, redactions=scrubbed.redactions)
    return ScrubValueResult(value=value, redactions={})
