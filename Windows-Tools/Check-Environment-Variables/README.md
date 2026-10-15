# Check-Environment-Variables

Tests the Windows **User** and **System** (Machine) environment variables and
writes a report. Read-only, apart from creating and deleting one temporary
variable as a write test. No Python or NX needed — just PowerShell.

## What it checks

| # | Check | Flags |
| --- | --- | --- |
| 1 | Every variable | empty value, leading/trailing spaces, `%VAR%` references to variables that don't exist |
| 2 | Path lists (`PATH`, `PSModulePath`, `UGII_PYTHONPATH`, any `;`-separated list of paths) | folders that don't exist, entries that are files, empty entries (stray `;`), quoted entries; duplicates are noted |
| 3 | Variables whose whole value is a path (e.g. `UGII_BASE_DIR`) | paths that don't exist |
| 4 | User vs System | variables set in both scopes with different values (the User value wins; `PATH` is merged) |
| 5 | This session | a stored value that differs from the one this session is using (needs a new sign-in/restart to take effect) |
| 7 | **NX baseline** (`FMS_HOME`, `JAVA_HOME`, `JRE_HOME`, `JRE64_HOME`) | not set, set at the wrong level (or overridden by a User value), a value different from the known-good one, a folder that doesn't exist, or a folder missing what NX needs (`bin\java.exe`, `bin`) |
| 6 | Write test | can a temporary variable be created, read back and deleted — User always, System only when run as administrator |

Values are read straight from the registry, so unexpanded `%VAR%` references are
visible. **PROBLEM** lines are counted in the `RESULT:` summary; **NOTE** lines
(duplicates, User/System differences, session differences) are informational.

## NX baseline

`nx-baseline.json` holds the known-good values for the four variables NX and
Teamcenter use, captured from a working workstation
(`Environment-report-20261015-132934.txt`):

| Variable | Level | Known-good value | Must contain |
| --- | --- | --- | --- |
| `FMS_HOME` | System | `C:\SPLM\TC2506\TCCS_PROD\tccs` | `bin` |
| `JAVA_HOME` | System | `C:\SPLM\Java\jre17` | `bin\java.exe` |
| `JRE_HOME` | System | `C:\SPLM\Java\jre17` | `bin\java.exe` |
| `JRE64_HOME` | System | `C:\SPLM\Java\jre17` | `bin\java.exe` |

Each run compares the machine against it. The end of the output
(and the report) gives a clear verdict:

```text
NX VARIABLES: PASS  -  all 4 are correct (FMS_HOME, JAVA_HOME, JRE_HOME, JRE64_HOME)
```

or, when something is wrong, which variable and why:

```text
NX VARIABLES: FAIL  -  1 of 4 wrong

  WRONG: JAVA_HOME
     found    : C:\Program Files\Java\jre8
     expected : C:\SPLM\Java\jre17   [System]
     problem  : JAVA_HOME is 'C:\Program Files\Java\jre8' but the baseline is 'C:\SPLM\Java\jre17'
     fix      : Set the System environment variable JAVA_HOME to 'C:\SPLM\Java\jre17' (needs an administrator).
```

Other, non-NX findings (e.g. a bad PATH entry) are listed separately under
`OTHER CHECKS` and don't change the NX verdict. The script's exit code is `2` when
the NX baseline fails, `0` otherwise, and `1` for an unexpected error. To change the baseline (for example
for a new Teamcenter or Java version), edit `nx-baseline.json`; `-BaselineFile
<path>` uses a different file, and the check is skipped if the file is missing.

## Usage

**Easiest: double-click `Run-Check.bat`.** It bypasses the PowerShell execution
policy (a `.ps1` from a zip is usually blocked, so running the `.ps1` directly
can flash an error and close) and keeps the window open at the end.

From a terminal instead:

```powershell
powershell -ExecutionPolicy Bypass -File .\Check-Environment-Variables.ps1
```

The report is saved in the **same folder as the script**
(`Environment-report-<timestamp>.txt`). The report **starts with the summary**: the
NX PASS/FAIL verdict and each wrong variable (found, expected, fix), followed by
the other findings; the full per-variable details come after a `FULL DETAILS
BELOW` line. Send that file to your support contact.

| Option | Meaning |
| --- | --- |
| `-SkipWriteTest` | Skip check 6 (the temporary-variable test). |
| `-BaselineFile <path>` | Baseline JSON to compare against (default: `nx-baseline.json` next to the script). |
| `-NoPause` | Don't wait for Enter at the end (otherwise the script waits when started from Explorer). |

If the script itself hits an unexpected error, it saves a partial report and shows
a window with the error and an **Exit** button.

## Notes

- To test the System scope's write test, run it from an administrator prompt; a
  normal run reports it as skipped, which is not an error.
- The temporary variable is named `HELION_ENVTEST_<random>` and is removed right
  after the test. If a failure message says it couldn't be deleted, remove it by
  hand in *Edit the system environment variables*.
- See also [Check-UGII-PythonPath](../Check-UGII-PythonPath/README.md), which
  focuses on the NX `UGII_PYTHONPATH` startup warning.
