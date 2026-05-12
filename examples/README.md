# agent-rec trace example

This directory contains synthetic trace fixtures. They are safe to share and contain fake data only.

Generate a report from the sample trace:

```bash
uv run agent-rec report examples/basic-trace.jsonl --out /tmp/agent-rec-example.html
open /tmp/agent-rec-example.html
```
