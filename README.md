# Helion NX Tools

NX Open (Python) automation and supporting tools for **NX 2506** running in
**Teamcenter managed mode** at Helion.

The repo is organized by **where the code runs** — inside NX, outside NX, or
recorded from NX as reference.

## Repository structure

```text
Helion-NX-Tools/
├── NX-Scripts/                  Scripts run INSIDE NX (File → Execute → NX Open…)
│   ├── Create-McMaster-Part/    McMaster-Carr COTS part creator (+ its .dlx dialogs)
│   │   └── README.md            How to set up and run the Create-McMaster-Part tool
│   ├── Check-Part-Exists/       Diagnostic: is an item id already in Teamcenter?
│   ├── List-Assembly-Components/ Write the assembly tree (components, bodies, materials) to a text file
│   ├── Color-By-Material/       Color every body by its NX material, from Materials/NX_Materials.csv
│   └── Export-System-Log/       Save a copy of the NX system log (syslog) to output/
├── my_scripts/                  YOUR OWN scripts: every *.py in here is git-ignored, never shared
├── lib/                         Shared helpers the NX scripts import (mcmaster, teamcenter, dialogs, assemblies, colors)
│   └── scraper/                 McMaster-Carr Selenium scraper (vendored; run OUTSIDE NX as a subprocess)
├── Windows-Tools/               Standalone Windows utilities (no NX or Python needed)
│   ├── NX-TC-Cache-Clear/       Batch script: kill NX/Teamcenter and clear local caches
│   │   └── README.md            What it clears and how to run it
│   ├── Check-Environment-Variables/  PowerShell: test User/System environment variables
│   └── Check-UGII-PythonPath/   PowerShell: diagnose the UGII_PYTHONPATH startup warning
├── Materials/                   NX material libraries (dated XML folders) and NX_Materials.csv, incl. a hex "color" column
├── output/                      Files the scripts write (git-ignored)
├── example_journals/            Journals RECORDED in NX, kept as reference only
├── setup.bat                    One-click setup: .venv + dependencies + NX Open MCP + McMaster login
├── setup_mcp.ps1                Called by setup.bat: extracts NX_Open_MCP.zip and writes .mcp.json
├── NX_Open_MCP.zip              NX Open API search MCP server (extracted to MCP/ by setup.bat)
├── MCP/                         Extracted MCP server (git-ignored)
├── requirements.txt             Python deps for the scraper (installed by setup.bat)
├── .venv/                       Python virtual environment (git-ignored)
├── HANDOFF.md                   Deep notes: key functions, gotchas, open items
└── README.md                    This file
```

## What lives where

| Folder | Runs | Contents |
|--------|------|----------|
| [NX-Scripts/](NX-Scripts/) | Inside NX (File → Execute → NX Open…) | The tools NX operators actually run, each in its own folder alongside its `.dlx` BlockStyler dialogs. |
| [my_scripts/](my_scripts/) | Inside NX | Personal scripts. Every `*.py` here is git-ignored, so nothing you write in this folder is shared or committed. Put shared tools under `NX-Scripts/` instead. |
| [Materials/](Materials/) | Not executed | Material library XMLs from the NX common library, plus `NX_Materials.csv` (one row per material; the `color` column is hand-maintained and drives Color-By-Material). `build_nx_materials_csv.py` rebuilds the CSV and keeps the colors. |
| [lib/](lib/) | Inside NX (imported by the NX scripts) | Helpers the NX scripts call: `mcmaster.py` (scraper wrapper, description/filename helpers), `teamcenter.py` (existence check, PDM error dump, Parasolid import), `vendor_part.py` (`create_vendor_part`, the BE9_COTS create), `nx_dialogs.py` (BlockStyler prompts), `layers.py` (`move_to_layer`), and `scraper/` (the Selenium scraper, run as an external subprocess since NX's embedded Python can't drive Edge). Scripts keep only the user-facing flow. |
| [Windows-Tools/](Windows-Tools/) | Outside NX (run directly in Windows) | Standalone troubleshooting utilities for the NX / Teamcenter workstation. They don't use the `.venv` or the NX Open scripts. |
| [example_journals/](example_journals/) | Not executed | Journals recorded via Tools → Journal → Record, kept for reverse-engineering NX Open calls. |

An NX script locates the repo root (the folder containing `lib/`) by walking up
the folder tree and adds it to `sys.path`, so it finds `lib/` and
`.venv/` no matter how deep it sits under `NX-Scripts/`.

## Tools

- **[Create McMaster Part](NX-Scripts/Create-McMaster-Part/README.md)** — enter a
  McMaster-Carr part number; it scrapes the product data, downloads the CAD,
  creates a `BE9_COTS` part in Teamcenter, and imports the geometry. See its
  [README](NX-Scripts/Create-McMaster-Part/README.md) for setup and usage.

- **[List Assembly Components](NX-Scripts/List-Assembly-Components/list_assembly_components.py)** —
  walks the displayed assembly and writes every component, its bodies and their
  NX material to `output/<part>_components.txt`, with a quantity-by-part summary.
- **[Color By Material](NX-Scripts/Color-By-Material/README.md)** — colors every
  body by its NX material using the hex codes in `Materials/NX_Materials.csv`.
  `color_by_material.py` clears assembly color overrides first;
  `color_by_material_asm_leave_color.py` leaves them. Modifies the component
  parts (not saved automatically).

- **[Export System Log](NX-Scripts/Export-System-Log/README.md)** — copies the running
  NX session's system log to `output/nx_syslog_<timestamp>.txt`, ready to attach to a
  ticket or send to support.

## Windows Tools

- **[NX-TC-Cache-Clear](Windows-Tools/NX-TC-Cache-Clear/README.md)** — batch
  script that stops NX and Teamcenter and clears their local caches when either
  is misbehaving.
- **[Check-Environment-Variables](Windows-Tools/Check-Environment-Variables/README.md)** —
  PowerShell script that tests the Windows User and System environment variables
  (missing paths, bad `%VAR%` references, PATH problems, User/System conflicts,
  write test) and saves a report. Double-click `Run-Check.bat`.
- **[Check-UGII-PythonPath](Windows-Tools/Check-UGII-PythonPath/README.md)** —
  diagnoses the NX "Unable to append module directory path in PYTHONPATH" warning.

## Getting started

1. Clone (or extract) this repo to a **short, plain folder**, e.g.
   `C:\Code\Helion-NX-Tools`. Avoid OneDrive, network drives, and paths with
   spaces or special characters — NX can fail with *"Unable to append module
   directory path in PYTHONPATH"* when a script is run from such a folder.
   `setup.bat` warns if the folder looks risky.
2. **Double-click** [setup.bat](setup.bat) — creates `.venv`, installs
   dependencies (behind the corporate SSL proxy), extracts the NX Open MCP
   server (`NX_Open_MCP.zip` → `MCP/`, registered in `.mcp.json`), and caches the
   McMaster login. Restart Claude Code in this folder afterwards so the `nxopen`
   server loads.
3. Follow the per-tool README under [NX-Scripts/](NX-Scripts/) to run a tool.
4. Put your own scripts in [my_scripts/](my_scripts/) — they are git-ignored.

## More detail

See [HANDOFF.md](HANDOFF.md) for the full list of NX Open / Teamcenter gotchas,
key functions, and open items.
