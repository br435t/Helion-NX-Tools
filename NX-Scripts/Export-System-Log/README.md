# Export System Log (NX Open)

NX Open (Python) script for **NX 2506**. It saves a copy of the running NX session's
**system log** (the "syslog") to a text file you can open, attach to a ticket, or
send to support.

Script: `NX-Scripts/Export-System-Log/export_syslog.py`

## Why

NX writes its system log to a temporary file whose name changes every session
(for example `C:\Users\<you>\AppData\Local\Temp\<you>4044196.syslog`). It holds the
machine and NX version header, startup messages, Teamcenter and licensing messages,
and any errors or warnings from the session, which is what support asks for. This
script finds that file for you and copies it somewhere easy to reach.

## Run it

1. Open **NX 2506** (any session; no part has to be open).
2. **File → Execute → NX Open…** and pick `export_syslog.py`.
3. The Listing Window shows where the log was copied from and to.

The copy is saved to the repo's **`output\`** folder, which is git-ignored:

```
output\nx_syslog_2026-10-19_144138.txt
```

Each run writes a **new timestamped file**, so earlier exports are never overwritten.

```
Exported NX system log (1,059,384 bytes)
  from: C:\Users\br435t\AppData\Local\Temp\br435t4044196.syslog
    to: C:\Code\Helion-NX-Tools\output\nx_syslog_2026-10-19_144138.txt
```

## Good to know

* **It is a snapshot.** The file is copied as it is at that moment. Anything NX has
  not yet written to disk may be missing, and anything logged afterwards is not in
  the copy. Run it again after reproducing a problem to capture it.
* **Export right after the problem.** Large sessions produce large logs (this one
  was about 1 MB), so a log exported later has more to dig through.
* **It is for the current session.** NX starts a new syslog each session, so the
  file for a crashed or closed session is not the one this script reads. Older
  session logs stay in your Temp folder until cleaned up.
* **The log can contain** your Windows user name, machine name, file paths and
  Teamcenter item ids. Check it before sharing outside Helion.

## If it fails

* **"NX system log not found"**: NX did not report a log file for this session.
  Check that logging is not turned off in your NX environment.
* **"Could not copy the system log"**: the message shows the Windows error and the
  source path. A locked file or a full disk are the usual causes; the source path
  is printed so you can open it directly.

## Files

* `export_syslog.py`: the script. It finds the repo root by walking up to the folder
  that contains `lib/`, the same way the other scripts here do, so it runs from
  wherever the repo is checked out.
* `output\nx_syslog_*.txt`: the exports (git-ignored).
