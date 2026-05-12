from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from .bundle import create_bundle
from .claude_hooks import write_claude_hook_event
from .events import read_trace
from .recorder import record_run
from .report import summarize, write_report

app = typer.Typer(no_args_is_help=True, help="Local-first flight recorder for coding agents.")
console = Console()


@app.command(context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def run(
    ctx: typer.Context,
    command: Annotated[list[str] | None, typer.Argument(help="Command to record, prefixed by --.")] = None,
    cwd: Annotated[Path, typer.Option(help="Working directory to run from.")] = Path.cwd(),
    trace_dir: Annotated[Path | None, typer.Option(help="Directory for JSONL traces.")] = None,
    use_pty: Annotated[bool, typer.Option("--pty", help="Allocate a pseudo-terminal for interactive CLI agents.")] = False,
) -> None:
    """Run a command while recording terminal output and git state."""
    full_command = command or ctx.args
    if full_command and full_command[0] == "--":
        full_command = full_command[1:]
    if not full_command:
        raise typer.BadParameter("provide a command after --")
    result = record_run(full_command, cwd=cwd, trace_dir=trace_dir, use_pty=use_pty)
    console.print(f"\n[bold]trace:[/bold] {result.trace_path}")
    raise typer.Exit(result.exit_code)


@app.command()
def report(
    trace: Annotated[Path, typer.Argument(help="Trace JSONL path.")],
    out: Annotated[Path, typer.Option("--out", "-o", help="HTML report output path.")] = Path("report.html"),
) -> None:
    """Generate a static HTML timeline report."""
    write_report(trace, out)
    console.print(f"wrote {out}")


@app.command()
def bundle(
    trace: Annotated[Path, typer.Argument(help="Trace JSONL path.")],
    out: Annotated[Path, typer.Option("--out", "-o", help="Bundle output path.")] = Path("agent-rec-bundle.tar.gz"),
) -> None:
    """Create a portable tar.gz repro bundle."""
    create_bundle(trace, out)
    console.print(f"wrote {out}")


@app.command("claude-hook")
def claude_hook(
    trace: Annotated[Path, typer.Option("--trace", help="Trace JSONL path to append to.")],
    session_id: Annotated[str, typer.Option("--session-id", help="agent-rec session id.")],
) -> None:
    """Append a Claude Code hook JSON payload from stdin to a trace."""
    payload = typer.get_text_stream("stdin").read()
    write_claude_hook_event(payload, trace, agent_rec_session_id=session_id)
    console.print(f"recorded Claude Code hook in {trace}")


@app.command()
def inspect(trace: Annotated[Path, typer.Argument(help="Trace JSONL path.")]) -> None:
    """Print a concise trace summary."""
    events = read_trace(trace)
    summary = summarize(events)
    table = Table(title="agent-rec trace")
    table.add_column("field")
    table.add_column("value")
    for key, value in summary.items():
        table.add_row(str(key), str(value))
    console.print(table)


if __name__ == "__main__":
    app()
