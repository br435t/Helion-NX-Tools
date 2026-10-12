# Create McMaster Part (NX Open)

NX Open (Python) automation for **NX 2506** in **Teamcenter managed mode**. Enter
a McMaster-Carr part number and it scrapes the product data, downloads the CAD,
creates a `BE9_COTS` part in Teamcenter, and imports the geometry — prompting
through BlockStyler dialogs along the way.

The main tool is `NX-Scripts/Create-McMaster-Part/CREATE_MCMASTER_PART.py` —
the McMaster/COTS flow (part number → scrape → create → import).

## Prerequisites

* **NX 2506** with an active **Teamcenter** session (managed mode).
* **Microsoft Edge** (pre-installed on Windows 10/11) — the scraper drives it.
* **Python 3.10+** on the machine (for the scraper). Get it from
  <https://www.python.org/downloads/> and tick *"Add python.exe to PATH"*.

## One-click setup


1. Download or clone this repo to a folder, e.g. `C:\Code\Create-McMaster-Part`.
2. **Double-click** `setup.bat`.

That creates the Python virtual environment the scraper needs, installs its
dependencies (works behind the corporate SSL proxy via `pip-system-certs`), and
opens a browser so you can log in to McMaster once. Re-running it is safe.

> `setup.bat` puts the environment in `.venv` at the repo root, and
> `CREATE_MCMASTER_PART.py` finds it automatically — no environment variables to
> set. Pass `nologin` (`setup.bat nologin`) to skip the McMaster login step.

## Create a part


1. Open **NX 2506** with a Teamcenter session.
2. **File → Execute → NX Open…** → select `NX-Scripts/Create-McMaster-Part/CREATE_MCMASTER_PART.py`.
3. Enter the **McMaster part number** when prompted.
4. The tool scrapes the product data, downloads the no-threads Parasolid CAD to
   `C:\TEMP\MCMASTER`, and shows a **Part Name** dialog pre-filled with the
   description (edit if you like).
5. It creates the `BE9_COTS` part, sets its attributes, and imports the CAD.
   Progress is written to the **Listing Window**.

Attributes set: `DB_PART_NO` = part number, `DB_PART_NAME` = the name you
confirm (pre-filled with the product title, all caps), `HE_Manufacturer` =
`MCMASTER`, `Part Class` = `Class III`. Creation is done by
`create_vendor_part` in `lib/vendor_part.py`.

Keep each script next to its `.dlx` dialog file(s); the scraper (`lib/scraper/`)
and `.venv` are found automatically at the repo root.

## Repository layout

The repo is organized by where code runs:

* `NX-Scripts/` — scripts the user runs **inside NX** (File → Execute → NX
  Open…). The main tool is
  `NX-Scripts/Create-McMaster-Part/CREATE_MCMASTER_PART.py` and its `.dlx`
  BlockStyler dialogs.
* `lib/` — shared helpers the NX scripts import (`mcmaster.py`, `teamcenter.py`,
  `nx_dialogs.py`). NX scripts keep only the user-facing flow; everything they
  call lives here. `lib/scraper/` is the McMaster-Carr Selenium scraper, run
  **outside NX** as a subprocess.
* `example_journals/` — journals **recorded in NX** (Tools → Journal →
  Record), kept as reference examples for reverse-engineering NX Open calls.
  Not executed directly.
* **Repo root** — `setup.bat` (one-click setup), `requirements.txt`, `.venv/`
  (Python env for the Tools; git-ignored), `README.md`, and `HANDOFF.md`.

| Path | Purpose |
|----|----|
| `setup.bat` | One-click setup: venv + dependencies + McMaster login. |
| `requirements.txt` | Python deps for the scraper (Selenium + the corporate-SSL helper). Installed by `setup.bat`. |
| `NX-Scripts/Create-McMaster-Part/CREATE_MCMASTER_PART.py` | Main tool: part number → scrape → create COTS part → import CAD. |
| `NX-Scripts/Create-McMaster-Part/*.dlx` | BlockStyler dialogs for the flow (part number, part name). |
| `lib/` | Shared helpers called by the NX scripts (scraper wrapper, Teamcenter create/check, dialogs). |
| `lib/scraper/` | Vendored McMaster-Carr scraper (Selenium). See `lib/scraper/VENDORED.md`. |
| `example_journals/` | Recorded NX journals used as reference (e.g. the working COTS-create). |
| `.venv/` | Python venv with Selenium (created by `setup.bat`; git-ignored). |
| `HANDOFF.md` | Deeper notes: key functions, gotchas, open items. |

An NX script locates the repo root by walking up the folder tree, so it finds
`lib/` and `.venv/` regardless of how deep it sits under `NX-Scripts/`.

## Notes

* Targets **Teamcenter managed mode** (not native/filesystem mode).
* If the part has **no downloadable CAD** (some raw stock and bulk items have no
  3-D Parasolid model, e.g. `5887K51`), the tool shows the reason and asks whether
  to create the part **without geometry**. **No** stops with nothing created in
  Teamcenter; **Yes** creates the part and skips the Parasolid import.
* The scraper needs a McMaster login (cached in a dedicated Edge profile). If the
  session expires, the tool opens a sign-in window automatically.
* See `HANDOFF.md` for the full list of NX Open / Teamcenter gotchas.


