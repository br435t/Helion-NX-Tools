# Check-UGII-PythonPath

Diagnoses the NX startup warning:

> Unable to append module directory path in PYTHONPATH. Please make sure that
> UGII_PYTHONPATH environment variable is correctly defined.

NX adds every folder in `UGII_PYTHONPATH` to Python's search path at startup. The
warning means one of those folders is missing or the value is malformed. The
value can come from two places, and the script reports on **both**:

1. **Windows environment variable** (User / Machine / current session): looks for
   folders that don't exist, empty entries (stray or trailing `;`), quote
   characters, and undefined `%VAR%` references.
2. **NX's own definition** in `<NX install>\UGII\ugii_env_ug.dat`: expands each
   `${VAR}` (e.g. `${UGII_PYTHON_HOME}`, `${UGCHECKMATE_DIR}`) and checks every
   resulting folder. A missing or incomplete NX install shows up here. It also
   lists launcher overrides (`UGII_ENV_FILE`, `UGII_CUSTOM_DIRECTORY_FILE`, ...)
   and flags override files or custom directories that don't exist.

## Usage

No Python or NX needed — just PowerShell.

**Easiest: double-click `Run-Check.bat`.** It bypasses the PowerShell execution
policy and keeps the window open at the end. (A `.ps1` that came from a zip or
download is usually *blocked* by Windows, so double-clicking or right-click →
*Run with PowerShell* on the `.ps1` itself just flashes an error and the window
closes. `Run-Check.bat` avoids that.)

Run it from the same launcher/shortcut NX is started from if you can, so
launcher-set variables are visible. From a terminal instead:

```powershell
powershell -ExecutionPolicy Bypass -File .\Check-UGII-PythonPath.ps1
```

It prints a report, marks each folder `ok` or `PROBLEM`, ends with a `RESULT:`
summary, and saves the report in the **same folder as the script**
(`UGII_PYTHONPATH-report-<timestamp>.txt`). Send that file to your support
contact.

| Option | Meaning |
| --- | --- |
| `-NxDir <folder>` | NX install folder (e.g. `C:\SPLM\NX\NX2506`). Auto-detected from `UGII_BASE_DIR` or `C:\SPLM\NX\*` if omitted. |
| `-NoPause` | Don't wait for Enter at the end (otherwise the script waits when started from Explorer). |
| `-Fix` | Rewrites only the **User**-level Windows variable without its bad entries, after saving a backup in the script's folder. Never edits NX files or the Machine-level variable. Close and reopen NX afterwards. |

If the script itself hits an unexpected error, it saves a partial report and shows
a window with the error and an **Exit** button, so the window doesn't just vanish.

## Reading the result

- **PROBLEM lines in Part 2** (`nxbin\python`, `Python312.zip`,
  `design_tools\checkmate\python`, `automated_testing\python`): those folders are
  missing from this NX install — it is incomplete or different from a working
  one. Reinstall/repair NX, or compare against a working machine.
- **PROBLEM lines in Part 1:** fix the Windows variable (`-Fix` for the User
  level; the Machine level needs an administrator).
- **Override files missing:** the launcher points `UGII_ENV_FILE` or
  `UGII_CUSTOM_DIRECTORY_FILE` at a file that isn't there — fix the launcher.

## Notes

- The Helion NX Tools scripts do **not** use `UGII_PYTHONPATH`; they add the repo
  root to the import path themselves. This warning is an NX environment issue,
  not a setup problem with this repo.
