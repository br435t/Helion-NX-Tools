# NX / Teamcenter Cache Clear

A Windows batch script that automates the manual cache-clearing procedure for
Siemens NX and Teamcenter. Use it when NX/TC is behaving oddly (stale sessions,
corrupt local cache, launch failures) and you need a clean state.

## What it does

[`Clear-NX-TC-Cache.bat`](Clear-NX-TC-Cache.bat) runs four steps:

1. **Stop NX** — kills `ugraf.exe`.
2. **Stop Teamcenter** — kills the Siemens PLM Java process (`javaw.exe` running
   from `C:\SPLM\Java\*`, the bundled Zulu JRE). Other Java applications are left
   untouched.
3. **Clear the Temp folder** — deletes the *contents* of `%LOCALAPPDATA%\Temp`
   (`C:\Users\<username>\AppData\Local\Temp`). Files and folders that are in use
   are skipped automatically; the `Temp` folder itself is kept.
4. **Remove profile cache folders** — deletes these from your user profile if
   they exist:
   - `%USERPROFILE%\Siemens`
   - `%USERPROFILE%\FCCCache`
   - `%USERPROFILE%\Teamcenter`

## Usage

1. Close NX and Teamcenter if you can (the script will force-kill them either way).
2. Double-click **`Clear-NX-TC-Cache.bat`**.
   - If you hit *access denied* errors, right-click → **Run as administrator**.
3. Review the on-screen results. The window pauses at the end so you can read the
   output before closing.

## Notes

- Items still locked by other running software are skipped, which is expected —
  only NX/TC-related content needs to be cleared.
- The original manual steps are preserved in [`instructions.txt`](instructions.txt).
- If your Siemens PLM Java install lives somewhere other than `C:\SPLM\Java`,
  update the path in Step 2 of the batch file.
