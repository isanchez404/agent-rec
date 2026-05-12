# agent-rec

Local-first flight recorder for coding agents.

`agent-rec` captures what terminal coding agents actually do: prompts, shell output, exit status, git diffs, changed files, and run metadata. It writes portable JSONL traces and static HTML reports that can be attached to bug reports, PRs, or future replay tools.

## Why

Generic LLM observability shows spans and model calls. Coding-agent debugging needs repo-native evidence:

- what command ran
- what changed in git
- whether tests ran
- what the terminal output showed
- what state the workspace ended in

## MVP commands

```bash
agent-rec run -- <command> [args...]
agent-rec report .agent-rec/sessions/<session>.jsonl --out report.html
agent-rec bundle .agent-rec/sessions/<session>.jsonl --out repro.tar.gz
agent-rec inspect .agent-rec/sessions/<session>.jsonl
```

## Development

```bash
uv sync --extra dev
uv run --extra dev pytest -q
uv run agent-rec --help
```

## Status

Early OSS scaffold. The first wedge supports generic CLI recording using subprocess capture plus git snapshots. Future adapters can add richer Claude Code/OpenCode/Hermes hooks.
