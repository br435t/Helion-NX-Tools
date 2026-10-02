<!-- fullWidth: false tocVisible: false tableWrap: true -->

# Custom Clear

edge://settings/privacy/cookies/AllCookies?searchSubpage=local

# Edge Cookie Clear

`clear_Edge-TC-cookies.ps1` deletes Microsoft Edge cookies whose host matches a search filter. It does the same job as searching `local` in\
`edge://settings/privacy/cookies/AllCookies?searchSubpage=local` and removing the results. The default filter is `local`, which covers\
`localhost` and `.local` hosts. Use it when stale local cookies cause Teamcenter web client login problems.

## What it does

1. Closes Edge, because the cookie database is locked while Edge is running.
2. Deletes every cookie whose host contains the filter text, in every Edge profile (Default, Profile N, Guest).
3. Relaunches Edge.

Cookies for other sites, saved passwords, history and bookmarks are not touched.

## Usage

```powershell
# Default: clear cookies matching "local"
powershell -ExecutionPolicy Bypass -File .\clear_Edge-TC-cookies.ps1

# Different filter
powershell -ExecutionPolicy Bypass -File .\clear_Edge-TC-cookies.ps1 -Filter teamcenter

# Leave Edge closed afterwards
powershell -ExecutionPolicy Bypass -File .\clear_Edge-TC-cookies.ps1 -NoRestart
```

| Parameter  | Description                                                      |
| ---------- | ---------------------------------------------------------------- |
| `-Filter`  | Text matched against the cookie host (substring). Default: `local` |
| `-NoRestart` | Do not relaunch Edge when finished                               |

## Notes

- The script never prompts: Edge is closed forcibly as soon as it runs. Save any open work (forms, unsent web content) first.
- No extra software is needed. The script reads and edits Edge's SQLite cookie database through `winsqlite3.dll`, which is built into Windows 10/11.
- Cookie files are looked up under `%LOCALAPPDATA%\Microsoft\Edge\User Data\<profile>\Network\Cookies`.
## Run nightly at midnight

Double-click `install_schedule.bat` (no admin rights needed). It creates a per-user scheduled task, `Clear Edge TC Cookies`, that runs the script daily at 12:00 AM with `-NoRestart`, and runs a missed job when the PC is next available. The task only runs while you are logged in.

To remove it, run `install_schedule.bat remove`.
