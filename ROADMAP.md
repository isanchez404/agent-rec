# Roadmap

`agent-rec` is a local-first flight recorder for coding agents. The near-term goal is to make coding-agent runs inspectable, shareable, and eventually replayable without requiring a hosted observability service.

## Phase 0: MVP foundation

Status: done

- Generic CLI recording via subprocess capture.
- JSONL event trace format.
- Git status/diff snapshots.
- Static HTML report.
- Scrubbed repro bundle.
- Claude Code hook ingestion.

## Phase 1: Better local recording

- PTY capture for interactive agents. Status: initial support added.
- Separate stdout/stderr streams when possible.
- Configurable output truncation.
- File-system change watching between events.
- Test command detection and annotations.
- Better git diff summaries for large repos.

## Phase 2: Agent adapters

Target adapters:

- Claude Code hooks.
- OpenCode session/tool events.
- Hermes Agent tool/session events.
- Aider git/session metadata.
- Codex CLI run metadata.

Adapter goals:

- Preserve original event payloads where safe.
- Normalize into `agent-rec.trace.v0` events.
- Scrub tool inputs before reports/bundles.
- Avoid requiring hosted services.

## Phase 3: Reports reviewers actually use

- Diff hunk timeline: connect file hunks to preceding events.
- Failed-command badges.
- Changed-without-test warnings.
- Changed-without-read warnings where adapters expose file reads.
- Self-contained HTML artifact suitable for PRs and issues.

## Phase 4: Repro bundle standard

- Bundle manifest.
- Bundle validation command.
- Dependency manifest capture.
- Redaction report.
- Dry-run replay timeline.
- Optional patch replay.

## Phase 5: Schema stabilization

- Publish `agent-rec.trace.v0` reference docs.
- Add JSON Schema.
- Add example traces.
- Add import/export helpers.
- Explore OpenTelemetry/OpenInference exporters without becoming another hosted observability product.

## Non-goals for now

- Building another coding agent.
- Building a hosted trace SaaS.
- Capturing secrets by default.
- Running untrusted replay bundles without sandboxing.
