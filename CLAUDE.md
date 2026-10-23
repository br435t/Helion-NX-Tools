# Helion NX Tools — rules for Claude

Repo overview: [README.md](README.md). Deep notes: [HANDOFF.md](HANDOFF.md).

## Script headers (every script under `NX-Scripts/` and `Windows-Tools/`)

Every script names its author and creation date in a header:

| Script type | Where the header goes | Format |
| --- | --- | --- |
| `NX-Scripts/**/*.py` | directly under the `# NX 2506` line | `# Author:  br435t` / `# Created: YYYY-MM-DD` |
| `Windows-Tools/**/*.bat` | directly under `@echo off` | `REM Author:  br435t` / `REM Created: YYYY-MM-DD` |
| `Windows-Tools/**/*.ps1` | top of the file | `# Author:  br435t` / `# Created: YYYY-MM-DD` |
| `Windows-Tools/**/*.ps1` that starts with a `<# ... #>` help block | **immediately after the closing `#>`** | same as above |

Python example:

```python
# NX 2506
# Author:  br435t
# Created: 2026-10-19
# <what the script does...>
```

* **PowerShell help blocks:** never put the header *above* a leading `<#` comment-based
  help block. That makes `Get-Help` ignore the block (it falls back to the bare syntax
  line). Put it right after `#>` instead, and check with `Get-Help <script>`.
* **New script:** add the header when you create the file. `Author` is the git user
  (`git config user.name`); `Created` is today's date as `YYYY-MM-DD`.
* **Existing script without a header:** use the date of its first commit
  (`git log --follow --diff-filter=A --format=%ad --date=short -- <file>`), or the
  file's creation date if it is not committed yet. Do not invent a date.
* **Never change `Author` or `Created` on an existing script**, even after edits.
  They record who first wrote it and when.
* Keep a file's existing line endings (CRLF or LF) when inserting the header.
* A recorded journal's own `# Journal created by ... on ...` line stays as it is,
  below the new header.

Out of scope: `my_scripts/` (personal, git-ignored), `NX-Scripts/ARCHIVE/`
(git-ignored), `lib/`, and non-script files such as READMEs and JSON.

## Personal scripts and their library functions (`my_scripts/`)

`my_scripts/` is the user's own space: every `*.py` in it is git-ignored and never shared.

* When the user asks for a **personal script**, write it in `my_scripts/`, not `NX-Scripts/`.
* Any reusable function written for a personal script goes in **`my_scripts/lib/`**, as a
  plain module such as `my_scripts/lib/my_helpers.py`, not in the shared top-level `lib/`.
  Only put code in the shared `lib/` when the user says it should be shared.
* **Never add an `__init__.py` to `my_scripts/lib/`.** It would make `lib` a package that
  shadows the shared `lib/` (NX puts a script's own folder first on `sys.path`) and break
  `from lib.assemblies import ...`. Import its modules by name after adding the folder to
  `sys.path`; the snippet is in `my_scripts/lib/README.md`.
* Name those modules so they don't clash with shared or standard-library modules
  (`assemblies`, `colors`, `teamcenter`, `os`, `csv`).
* Personal scripts and `my_scripts/lib/` modules do not need the Author/Created header
  (out of scope above), though adding one is fine.

## NX material library (loading and assigning materials)

Helion's NX materials are **not** in NX's built-in library. They are two MatML files in the shared
NXcustom folder `\\usantpvwtcor001\NXStore\NX_PROD_CUSTOM\NXcustom\NXcommonlibrary\Materials\`:
`helion_material_library.xml` (the registered Site MatML Library) and
`Gas_and_Liquid_helion_material_library.xml`. `Materials/NX_Materials.csv` was built from them; its
`source_file` column says which file each material is in.

* NX's default library is switched off at the site (`UG_NxMaterialLibraryEnable=0` in
  `NX2506library\CustomerDefaults\Site\startup\nx_site.dpv` on that share), so
  `PhysicalMaterialCollection.LoadFromNxmatmllibrary(name)` **fails** with "No object found with this
  name". Load with `LoadFromMatmlLibrary(<library file>, <name>)`, then `AssignObjects([body])`.
* Use `lib/assemblies.py::assign_material` for this; the folder is `MATERIAL_LIBRARY_DIR` in
  `lib/color_by_material.py`. To check how NX is configured, read `nx_site.dpv`; do not guess.

## Creating geometry: use the Builder so it appears in the feature tree

When an NX Open script creates or modifies geometry (curves, splines, extrudes, holes, blends,
datums, ...), **use the feature Builder API whenever one exists**, so the result is a real feature
in the Part Navigator feature tree: parametric, editable by the user, and undoable as one step.
Do not build it with the direct-creation collections (for example `part.Curves.Create...`,
`part.Points.Create...` used alone, or UF calls) when a Builder can do the same job. Those make
unparameterized objects that never show up as features and cannot be edited afterwards.

* **Pattern** (as in the recorded journals in `example_journals/`, e.g. `journal_create_vendor_part.py`):
  `builder = part.Features.Create<Thing>Builder(...)`, set its properties, `builder.Commit()`, and
  always `builder.Destroy()` in a `finally`. Wrap the commit in an undo mark
  (`session.SetUndoMark(...)`, `UndoToMark(...)` if it fails) so a failure leaves nothing behind.
* **Find the Builder first:** look for a recorded journal in `example_journals/` (or ask the user to
  record one with Tools > Journal > Record), then check the NX Open stubs/docs
  (`Create...Builder` on `part.Features`). Journals show the exact property order NX needs.
* Helper objects a Builder takes as input (for example the `Point` objects behind a studio spline's
  through-points, or sketch/curve sections) may be plain objects; that is fine. The *result* is what
  must be a feature.
* If no Builder exists for the operation, a direct call is acceptable: say so in the script's header
  comment so the user knows the result will not be in the feature tree.
* Examples in this repo that follow the pattern: `lib/vendor_part.py::create_vendor_part` (File > New
  Item) and `lib/colors.py::clear_component_color_override` (properties builder: create, set, `Commit`,
  `Destroy` in a `finally`).

