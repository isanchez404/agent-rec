# Contributing

Thanks for helping improve `agent-rec`.

The project is early, so the most valuable contributions are small, well-tested improvements to the local recording path, trace schema, reports, scrubbing, and agent adapters.

## Development setup

```bash
git clone https://github.com/isanchez404/agent-rec.git
cd agent-rec
uv sync --extra dev
uv run --extra dev pytest -q
```

## Development principles

- Keep the CLI thin; put behavior in testable modules under `src/agent_rec/`.
- Prefer local-first behavior. Do not require hosted services for core functionality.
- Do not leak secrets in reports, bundles, examples, tests, or logs.
- Preserve raw local evidence where useful, but scrub shareable artifacts by default.
- Keep the trace format simple JSONL unless there is a strong reason otherwise.

## Testing

Run the full suite before opening a PR:

```bash
uv run --extra dev pytest -q
```

For new behavior, add tests first where practical. Existing tests live under `tests/`.

## Good first issues

- Add more secret scrubbing patterns.
- Improve report layout and diff readability.
- Add example traces under `examples/`.
- Add JSON Schema for `agent-rec.trace.v0`.
- Add adapter experiments for OpenCode, Hermes, Aider, or Codex CLI.

## Security

Do not include real tokens, private repo data, proprietary source code, or user transcripts in fixtures. Use synthetic traces and fake secrets only.

If you find a security issue, please avoid posting exploit details in a public issue until there is a maintainer response.
