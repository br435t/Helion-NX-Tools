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
│   └── Check-Part-Exists/       Diagnostic: is an item id already in Teamcenter?
├── lib/                         Shared helpers the NX scripts import (mcmaster, teamcenter, dialogs)
│   └── scraper/                 McMaster-Carr Selenium scraper (vendored; run OUTSIDE NX as a subprocess)
├── Windows-Tools/               Standalone Windows utilities (no NX or Python needed)
│   └── NX-TC-Cache-Clear/       Batch script: kill NX/Teamcenter and clear local caches
│       └── README.md            What it clears and how to run it
├── example_journals/            Journals RECORDED in NX, kept as reference only
├── setup.bat                    One-click setup: .venv + dependencies + McMaster login
├── requirements.txt             Python deps for the scraper (installed by setup.bat)
├── .venv/                       Python virtual environment (git-ignored)
├── HANDOFF.md                   Deep notes: key functions, gotchas, open items
└── README.md                    This file
```

## What lives where

| Folder | Runs | Contents |
|--------|------|----------|
| [NX-Scripts/](NX-Scripts/) | Inside NX (File → Execute → NX Open…) | The tools NX operators actually run, each in its own folder alongside its `.dlx` BlockStyler dialogs. |
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

## Windows Tools

- **[NX-TC-Cache-Clear](Windows-Tools/NX-TC-Cache-Clear/README.md)** — batch
  script that stops NX and Teamcenter and clears their local caches when either
  is misbehaving.

## Getting started

1. Clone this repo to a local folder, e.g. `C:\Code\Helion-NX-Tools`.
2. **Double-click** [setup.bat](setup.bat) — creates `.venv`, installs
   dependencies (behind the corporate SSL proxy), and caches the McMaster login.
3. Follow the per-tool README under [NX-Scripts/](NX-Scripts/) to run a tool.

## More detail

See [HANDOFF.md](HANDOFF.md) for the full list of NX Open / Teamcenter gotchas,
key functions, and open items.
