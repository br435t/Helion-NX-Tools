# Env Probe (NX Open)

NX Open (Python) diagnostic for **NX 2506**. It prints what NX itself sees when it runs
a script: the script's folder, the Python NX is using, the `UGII_*` environment
variables, and every entry in `UGII_PYTHONPATH`, `PYTHONPATH` and `sys.path`, each
marked `ok` or `MISSING`.

Script: `NX-Scripts/Env-Probe/env_probe.py`

## Why

NX sometimes shows **"Unable to append module directory path in PYTHONPATH"** when a
script is run. The cause is usually the folder the script lives in or a broken
path entry, such as a very long or non-ASCII path, spaces, a network share or OneDrive
folder, or an entry in `UGII_PYTHONPATH` that no longer exists. This script shows
those things from inside NX, which a normal Windows command prompt cannot. Its
companion `Windows-Tools/Check-UGII-PythonPath` checks the same problem from outside NX.

## Run it

1. Open **NX 2506** (no part needs to be open).
2. **File → Execute → NX Open…** and pick `env_probe.py`.
3. Read the Listing Window.

It imports nothing from `lib/`, so it runs from **any folder**. That is what makes it
useful for isolating the problem:

1. Run it from its place in the repo and note the output.
2. Copy `env_probe.py` to a short, plain folder such as `C:\Temp` and run it again.
3. Compare the two. If the warning only appears for one location, that folder is the cause.

## What the output shows

| Section | What it tells you |
| --- | --- |
| **Script file / folder** | Where NX loaded the script from, and whether that path has the usual troublemakers: length in characters, non-ASCII characters, spaces, UNC/network (`\server\...`), OneDrive |
| **Python / Executable** | The Python version NX runs the script with, and that it is NX's own `ugraf.exe` and not a separately installed Python |
| **Environment** | `UGII_BASE_DIR`, `UGII_ROOT_DIR`, `UGII_PYTHON_HOME`, `UGII_ENV_FILE`, `UGII_CUSTOM_DIRECTORY_FILE`, `UGII_USER_DIR`, `UGII_USER_PROFILE_DIR`, `PYTHONHOME`, or `(not set)` |
| **UGII_PYTHONPATH / PYTHONPATH** | Every `;`-separated entry, numbered. `MISSING` is a folder that does not exist, `EMPTY` is a blank entry (for example from a doubled or trailing `;`), `ok` exists. `.zip` entries are accepted if the file exists |
| **sys.path** | The final list Python searches, with the same `ok` / `MISSING` marks |
| **Repo root** | The folder containing `lib/`, found by walking up from the script, or `NOT FOUND` if the script is not inside the repo |

## What a healthy run looks like

`working_envprobe.txt` in this folder is a saved run from a working setup (NX 2506,
repo at `C:\Code\Helion-NX-Tools`): a short ASCII path with no spaces, `UGII_PYTHONPATH`
and `PYTHONPATH` both `(not set)`, every `sys.path` entry `ok`, and the repo root found.
Compare your own output against it.

## What to look for

* **`MISSING` or `EMPTY` entries** in `UGII_PYTHONPATH` or `PYTHONPATH`: remove or fix them.
  A leftover entry is the most common cause of the warning.
* **`has spaces`, `non-ASCII`, `UNC/network` or `OneDrive` as `True`** for the script folder:
  move the repo to a short, plain local folder, for example `C:\Code\Helion-NX-Tools`.
* **A `UGII_ENV_FILE` or `UGII_CUSTOM_DIRECTORY_FILE` on a network share** is normal at
  Helion (the shared NX customization), but a share that is unreachable can also cause
  slow or odd startups. Note whether the path is reachable.
* **Repo root `NOT FOUND`**: the script was run from outside the repo, which is fine for
  the probe itself but means the repo's other scripts would not find `lib/` from there.

## Good to know

* **Read-only.** It only prints information; it changes nothing and writes no files.
* **It reports one session.** The values are those of the NX session running the script.
  Start NX fresh after changing an environment variable to see the new values.

## Files

* `env_probe.py`: the script
* `working_envprobe.txt`: sample output from a working setup, for comparison
