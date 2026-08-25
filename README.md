# MECH2700

[![Checks](https://github.com/keys-i/MECH2700/actions/workflows/checks.yml/badge.svg)](https://github.com/keys-i/MECH2700/actions/workflows/checks.yml)
[![Release](https://github.com/keys-i/MECH2700/actions/workflows/release.yml/badge.svg)](https://github.com/keys-i/MECH2700/actions/workflows/release.yml)

Weekly exercises, lectures, tutorials, and assignments for MECH2700.

## Setup

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and
   [Tectonic](https://tectonic-typesetting.github.io/book/latest/installation/).
2. Clone and sync:

```bash
git clone https://github.com/keys-i/MECH2700.git
cd MECH2700
uv sync
```

That creates `.venv` and installs project dependencies (Python ≥ 3.12).

## Weekly exercises

| Folder | Contents |
| ------ | -------- |
| `prac/` | Practical scripts and write-ups (`week_01.py`, `week_01.tex`, …) |
| `lec/` | Lecture code (`week_01.py`, …) |
| `assign/` | Assignments |

## Run codes

Interactive menu (Lecture / Practical → week):

```bash
uv run code
```

Or run a file directly:

```bash
uv run python prac/week_01.py
uv run python lec/week_01.py
```

### Other commands

```bash
uv run clean                 # remove gitignored build artefacts (keeps .venv)
uv run fmt [py|tex]          # format all files, or one language
uv run latex-compile path.tex  # compile with Tectonic
uv run lint [py|tex]         # lint all files, or one language
uv run typecheck             # type-check Python files
```
That creates `.venv` and installs project dependencies (Python ≥ 3.12).

## Weekly exercises

| Folder | Contents |
| ------ | -------- |
| `prac/` | Practical scripts and write-ups (`week_01.py`, `week_01.tex`, …) |
| `lec/` | Lecture code (`week_01.py`, …) |
| `tuts/` | Tutorials (`W<number>/`) |
| `assign/` | Assignments |

## Run codes

Interactive menu (Lecture / Practical → week):

```bash
uv run code
```

Or run a file directly:

```bash
uv run python prac/week_01.py
uv run python lec/week_01.py
```

### Other commands

```bash
uv run clean                 # remove gitignored build artefacts (keeps .venv)
uv run latex-compile path.tex  # compile with MacTeX, strip aux files
```
