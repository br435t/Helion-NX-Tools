<!-- fullWidth: false tocVisible: false tableWrap: true -->
# my_scripts/my_journals

Your own recorded NX journals. Like the rest of `my_scripts/`, every `*.py` file in here is\
git-ignored, so your journals stay on your machine. Only this README is tracked, so the folder\
exists after a clone.

## Record one

1. In NX: **Tools → Journal → Record** (or *Application → Journal → Record*).
2. When asked where to save, choose a `.py` file in this folder, for example\
   `my_scripts\my_journals\journal_my_task.py`.
3. Do the steps in NX, then **Stop Recording**.

## Replay one

**File → Execute → NX Open…** \[Alt+f8\] and pick the journal. (Or Tools → Journal → Play.)

## Good to know

- **Recorded journals are for reference, and rarely run well unedited.** They hard-code object\
  names, selections and dialog state, so a replay on a different part may fail. They are most\
  useful for finding the NX Open call behind a menu action, which is how\
  `example_journals/` is used in this repo.
- **Journals worth sharing** belong in `example_journals/` (committed, reference only) or, if you\
  turn one into a real tool, in `NX-Scripts/` with a README and the Author/Created header.
- **Turning a journal into a script:** keep the calls you need, drop the undo marks and the\
  `Dialog Begin` comments, and put reusable pieces in `my_scripts/lib/` (see its README).
- No `__init__.py` here either: it is a folder of standalone files, not a package.