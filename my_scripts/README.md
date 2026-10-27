# my_scripts

Your own NX scripts. Nothing in here is shared: every `*.py` file in this folder
(and its subfolders) is git-ignored, so it stays on your machine and never
shows up in `git status` or a commit.

Company-shared NX scripts live under `NX-Scripts/`. Anything
that should be shared belongs there instead (move it out of `my_scripts` and
commit it).

Scripts here can import the shared helpers in `lib/` the same way the shared
scripts do: walk up from the script to the folder containing `lib/` and add it to
`sys.path` (see `NX-Scripts/Color-By-Material/color_by_material.py` for the
snippet).

Your own reusable functions go in [lib/](lib/), also git-ignored. It has no
`__init__.py` on purpose; see [lib/README.md](lib/README.md) for how to import from it.

Your recorded NX journals go in `example_journals/` at the repo root (one git-ignored folder for all journals,
not inside `my_scripts/`).
