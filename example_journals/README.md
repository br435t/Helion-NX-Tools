# example_journals

Your recorded NX journals, kept as reference for finding the NX Open call behind a menu action.
Everything in this folder **except this README is git-ignored**, so your journals stay on your machine
(they are not committed, pushed, or shipped in a release). The folder itself is in the repo so it exists after a clone.

## Record one

1. In NX: **Tools → Journal → Record**.
2. Save the `.py` file in this folder, for example `example_journals\journal_my_task.py`.
3. Do the steps in NX, then **Stop Recording**.

## Good to know

- Recorded journals hard-code object names and selections, so they rarely replay cleanly on another part. Their value is
  showing the exact calls and property order NX uses. The repo rules (CLAUDE.md) say to check here first before writing
  NX Open geometry code.
- Turn a journal into a real tool by keeping the calls you need and dropping the undo marks and `Dialog Begin`
  comments; put the script in `NX-Scripts/` (shared) or `my_scripts/` (personal).
