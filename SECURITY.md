# Security Policy

`agent-rec` handles command output, tool payloads, diffs, and traces that may contain secrets or private source code.

## Supported versions

The project is pre-1.0. Please use the latest `main` branch until releases begin.

## Reporting a vulnerability

If you find a security issue, please contact the maintainer privately before opening a public issue with exploit details.

Include:

- affected version or commit
- reproduction steps
- expected vs actual behavior
- whether secrets/private data can leak

## Secret handling expectations

- Raw traces are local evidence and may contain sensitive data.
- Reports and bundles should scrub common secrets by default.
- Tests and examples must use fake secrets only.
- Repro bundles from untrusted sources should not be executed without sandboxing.
