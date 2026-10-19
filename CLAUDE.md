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

`Windows-Tools/NX-TC-Cache-Clear/` is a separate git repo (a gitlink here), so a
header added to its script must be committed there and the pointer updated here.
