"""Project command entry points."""

from __future__ import annotations

import os
import re
import sys
import termios
import tty
from argparse import ArgumentParser
from pathlib import Path
from select import select
from statistics import mode
from subprocess import call

from rich.console import Console

console = Console()
ROOT = Path.cwd()
KINDS = {
    "Lecture": ROOT / "lec",
    "Practical": ROOT / "prac",
    "Assignment": ROOT / "assign",
}


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


def _language_args() -> tuple[str | None, list[str]]:
    args = sys.argv[1:]
    language = args.pop(0) if args and args[0] in {"py", "tex"} else None
    return language, args


def fmt() -> int:
    language, args = _language_args()
    python = 0 if language == "tex" else call(["ruff", "format", *args, "."])
    tex = 0 if language == "py" else call(["badness", "format", *args, "."])
    return python or tex


def lint() -> int:
    language, args = _language_args()
    python = 0 if language == "tex" else call(["ruff", "check", *args, "."])
    tex = 0 if language == "py" else call(["badness", "lint", *args, "."])
    return python or tex


typecheck = lambda: call(["basedpyright", *sys.argv[1:]])


def _menu(
    title: str,
    options: list[str],
    choices: list[list[str]] | None = None,
) -> tuple[int, int] | None:
    """Return item and choice indexes, or None to go back"""
    choices = choices or [[""] for _ in options]

    if not sys.stdin.isatty() or not sys.stdout.isatty():
        while True:
            console.print(f"[bold cyan]{title}[/]")
            for i, option in enumerate(options, 1):
                console.print(f"  [cyan]{i}.[/] {option}")
            try:
                raw = console.input("[cyan]Select (Esc: back):[/] ").strip()
            except EOFError:
                return None
            if raw.lower() in {"\x1b", "esc"}:
                return None
            if raw.isdecimal() and 1 <= int(raw) <= len(options):
                idx = int(raw) - 1
                selected = (
                    _menu("Version", choices[idx])
                    if len(choices[idx]) > 1
                    else (0, 0)
                )
                if selected is not None:
                    return idx, selected[0]
            else:
                console.print("[red]invalid[/]")

    idx, choice, fd = 0, 0, sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

    try:
        tty.setcbreak(fd)
        while True:
            console.print(f"[bold cyan]{title}[/]")
            for i, option in enumerate(options):
                label = (
                    f" [yellow]< {choices[i][choice]} >[/]"
                    if i == idx and len(choices[i]) > 1
                    else ""
                )
                marker, style = (
                    ("❯", "bold green") if i == idx else (" ", "dim")
                )
                console.print(f"  [{style}]{marker} {option}[/]{label}")
            ch = os.read(fd, 1)
            if ch == b"\x1b":
                for _ in range(2):
                    if not select([fd], [], [], 0.05)[0]:
                        break
                    ch += os.read(fd, 1)
            sys.stdout.write(f"\033[{len(options) + 1}A\033[J")
            sys.stdout.flush()
            if ch in (b"\r", b"\n"):
                console.print(
                    f"[cyan]{title}[/] {options[idx]} {choices[idx][choice]}"
                )
                return idx, choice
            if ch in (b"\x1b[A", b"\x1b[B"):
                idx = (idx + (1 if ch.endswith(b"B") else -1)) % len(options)
                choice = 0
            elif ch in (b"\x1b[C", b"\x1b[D"):
                choice = (choice + (1 if ch.endswith(b"C") else -1)) % len(
                    choices[idx]
                )
            elif ch in (b"", b"\x1b"):
                return None
            elif ch in (b"q", b"Q"):
                raise SystemExit(1)
    finally:
        # Discard leftover menu keystrokes before the next input prompt
        termios.tcsetattr(fd, termios.TCSAFLUSH, old)
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()


def _scripts(folder: Path) -> dict[str, list[Path]]:
    """Group choices under the most common numbered filename prefix"""
    groups: dict[tuple[str, str], list[Path]] = {}
    for path in sorted((*folder.glob("*.py"), *folder.glob("[!.]*/*.py"))):
        match = re.fullmatch(r"(.*[^0-9])([0-9]+)", path.stem.split(".")[0])
        if path.is_file() and match:
            groups.setdefault((match[1], match[2]), []).append(path)
    if not groups:
        return {}
    prefix = mode(name for name, _ in sorted(groups))
    label = prefix.replace("_", " ").replace("-", " ").strip().title()
    return {
        f"{label} {number}": sorted(
            paths, key=lambda p: (p.parent != folder, "." in p.stem)
        )
        for (name, number), paths in sorted(
            groups.items(), key=lambda p: int(p[0][1])
        )
        if name == prefix
    }


def _version(path: Path, folder: Path) -> str:
    version = path.stem.partition(".")[2]
    if path.parent != folder:
        version = f"{path.parent.name}/{version}".rstrip("/")
    return version.lower()


def _pick_script(folder: Path) -> Path | None:
    entries = _scripts(folder)
    if not entries:
        console.print(f"[red]no scripts in {folder}[/]")
        return None
    choices = [
        [
            "Advanced"
            if (name := _version(p, folder)) == "adv"
            else name.replace("_", " ").title() or "Normal"
            for p in paths
        ]
        for paths in entries.values()
    ]
    selected = _menu(
        next(iter(entries)).rsplit(" ", 1)[0], list(entries), choices
    )
    if selected is None:
        return None
    index, choice = selected
    return list(entries.values())[index][choice]


def code() -> int:
    parser = ArgumentParser(description="Run a script or open the menu")
    parser.add_argument(
        "target",
        nargs="?",
        help="lec/week, prac/week or assign/assignment/task",
    )
    parser.add_argument(
        "mode",
        nargs="?",
        default="norm",
        help="filename suffix or subfolder (default: norm)",
    )
    args = parser.parse_args()
    if args.target is not None:
        folder_name, _, number = args.target.rpartition("/")
        folder = ROOT / folder_name
        if folder == KINDS["Assignment"]:
            folder = folder / "1"
        valid_folder = folder in (KINDS["Lecture"], KINDS["Practical"]) or (
            folder.parent == KINDS["Assignment"] and folder.name.isdecimal()
        )
        if not valid_folder or not number.isdecimal():
            parser.error(
                "use lec/week, prac/week or assign/assignment/task "
                "(assign/task selects assignment 1)"
            )
        suffix = {"norm": "", "normal": "", "advanced": "adv"}.get(
            args.mode, args.mode
        )
        script = next(
            (
                path
                for label, paths in _scripts(folder).items()
                if int(label.rsplit(" ", 1)[1]) == int(number)
                for path in paths
                if _version(path, folder) == suffix
            ),
            None,
        )
        if script is None:
            parser.error(f"no {args.mode} script for {args.target}")
    else:
        kinds = list(KINDS)
        script = None
        while script is None:
            kind = _menu("Type", kinds)
            if kind is None:
                return 0
            folder = KINDS[kinds[kind[0]]]
            if folder == KINDS["Assignment"]:
                assignments = sorted(
                    (
                        p
                        for p in folder.glob("[0-9]*")
                        if p.name.isdecimal() and p.is_dir()
                    ),
                    key=lambda p: int(p.name),
                )
                if not assignments:
                    console.print(f"[red]no assignments in {folder}[/]")
                    continue
                labels = [f"Assignment {p.name}" for p in assignments]
                while script is None:
                    selected = _menu("Assignment", labels)
                    if selected is None:
                        break
                    script = _pick_script(assignments[selected[0]])
            else:
                script = _pick_script(folder)
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
    rc = call(
        [
            "tectonic",
            "-X",
            "compile",
            "-Z",
            "shell-escape-cwd=.",
            tex.name,
        ],
        cwd=tex.parent,
    )
    console.print(
        ("[green]ok[/]" if rc == 0 else "[red]failed[/]")
        + f" {tex.with_suffix('.pdf').name}"
    )
    return rc
