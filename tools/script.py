"""Project command entry points."""

from __future__ import annotations

import os
import re
import sys
import termios
import tty
from pathlib import Path
from subprocess import call

from rich.console import Console

console = Console()
ROOT = Path.cwd()
TEXBIN = Path("/Library/TeX/texbin")
WEEK_RE = re.compile(r"week_(\d+)\.py\Z")
KINDS = {"Lecture": ROOT / "lec", "Practical": ROOT / "prac"}


clean = lambda: call(
    [
        "git",
        "clean",
        "-fdX",
        "--",
        ".git",
        *(p.name for p in ROOT.iterdir() if p.name != ".venv"),
    ]
)


def _menu(title: str, options: list[str]) -> int:
    def render(idx: int) -> None:
        console.print(f"[bold cyan]{title}[/]")
        for i, option in enumerate(options):
            if i == idx:
                console.print(f"  [bold green]❯ {option}[/]")
            else:
                console.print(f"    [dim]{option}[/]")

    def wipe() -> None:
        sys.stdout.write(f"\033[{len(options) + 1}A\033[J")
        sys.stdout.flush()

    if not sys.stdin.isatty() or not sys.stdout.isatty():
        console.print(f"[bold cyan]{title}[/]")
        for i, option in enumerate(options, 1):
            console.print(f"  [cyan]{i}.[/] {option}")
        while True:
            raw = console.input("[cyan]Select:[/] ").strip()
            if raw.isdigit() and 1 <= int(raw) <= len(options):
                return int(raw) - 1
            console.print("[red]invalid[/]")

    idx, fd = 0, sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

    try:
        tty.setcbreak(fd)
        render(idx)
        while True:
            ch = sys.stdin.read(1)
            if ch in "\r\n":
                wipe()
                console.print(f"[cyan]{title}[/] [green]{options[idx]}[/]")
                return idx
            if ch == "\x1b":
                seq = sys.stdin.read(2)
                if seq == "[A":
                    idx = (idx - 1) % len(options)
                elif seq == "[B":
                    idx = (idx + 1) % len(options)
                else:
                    continue
                wipe()
                render(idx)
            elif ch in "qQ":
                wipe()
                raise SystemExit(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()


def _weeks(folder: Path) -> dict[str, Path]:
    weeks: dict[str, Path] = {}
    if not folder.is_dir():
        return weeks
    for path in sorted(folder.glob("week_*.py")):
        match = WEEK_RE.fullmatch(path.name)
        if match:
            weeks[f"Week {int(match.group(1)):02d}"] = path
    return weeks


def code() -> int:
    kind = list(KINDS)[_menu("Type", list(KINDS))]
    weeks = _weeks(KINDS[kind])
    if not weeks:
        console.print(f"[red]no week_XX.py in {KINDS[kind]}[/]")
        return 1
    week = list(weeks)[_menu("Week", list(weeks))]
    script = weeks[week]
    console.print(f"[dim]running[/] [bold]{script.relative_to(ROOT)}[/]")
    return call([sys.executable, str(script)], cwd=ROOT)


def latex_compile() -> int:
    if len(sys.argv) < 2:
        console.print("[red]usage:[/] uv run latex-compile <path.tex>")
        return 2
    tex = Path(sys.argv[1]).expanduser().resolve()
    if tex.suffix != ".tex" or not tex.is_file():
        console.print(f"[red]not a .tex file:[/] {tex}")
        return 2
    env = {
        **os.environ,
        "PATH": f"{TEXBIN}{os.pathsep}{os.environ.get('PATH', '')}",
    }
    latexmk = str(TEXBIN / "latexmk")
    flags = (
        "-pdf",
        "-interaction=nonstopmode",
        "-halt-on-error",
        "-quiet",
        tex.name,
    )
    rc = call([latexmk, *flags], cwd=tex.parent, env=env)
    call([latexmk, "-c", "-quiet", tex.name], cwd=tex.parent, env=env)
    console.print(
        ("[green]ok[/]" if rc == 0 else "[red]failed[/]")
        + f" {tex.with_suffix('.pdf').name}"
    )
    return rc
