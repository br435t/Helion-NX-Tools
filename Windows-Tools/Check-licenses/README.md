# Check-licenses

Shows who is using the NX license features (NX91110, `nx_design_token`,
Teamcenter modules, ...) on the Helion license server, and saves a report.
Windows only; nothing here needs NX or the repo's Python environment.

## Run it

Double-click **`CheckLicenses.bat`**. It runs `CheckLicenses.ps1`, prints the full
report in the window, and waits for a key press (`pause`) so you can read it.

Needs `C:\SPLM\NX\NX2506\UGFLEXLM\lmutil` (installed with NX 2506) and a network
route to the license server. It only reads status; it does not check anything out
or change anything.

## What you get

The report is printed and saved to `output\license_status_latest.txt` at the repo
root (overwritten each run):

```
NX license usage report
Server: 28000@USANTPVWTCOR001.HE.local
Generated: 2026-10-17 13:10:47
----------------------------------------

In use by br435t:
    teamcenter_author
    nx_design_token  nx_partitions  (2 licenses)

NX91110 (30/52)
    sa562b
    swilliams
    ...

nx_design_token (133/300)
    sa562b
    ...
```

* **Header:** title, server, and the date and time the report was generated.
* **In use by <you>:** every feature held by the Windows account running the script
  (the match ignores upper/lower case), with the module name and license count
  where the server gives them. Shows `(nothing)` if your account holds none.
* **One block per feature in use:** the feature name, `(licenses in use / issued)`,
  then each user on their own line. Features nobody is using are left out.

The full, unedited `lmutil lmstat -a` output is saved next to it as
`output\license_status_raw.txt` (overwritten each run).

### Reading the numbers

The count in parentheses is **licenses**, not people. One person can hold several:
a single `nx_design_token` or `adv_assemblies` checkout can be 2 to 26 licenses, so
the count will usually be higher than the number of names listed.

## If it fails

If the server does not answer, the script prints what `lmutil` said (for example
`No socket connection to license server manager`) and **leaves the last good
report files untouched**, so a failed run never replaces real data with an error.
Check that you are on the company network or VPN and try again.

## Options

Run the script directly in PowerShell for these:

```
powershell -ExecutionPolicy Bypass -File CheckLicenses.ps1 [-Server <port@host>] [-LmUtil <path>] [-InputFile <file>]
```

| Option | Default | Use |
| --- | --- | --- |
| `-Server` | `28000@USANTPVWTCOR001.HE.local` | A different license server |
| `-LmUtil` | `C:\SPLM\NX\NX2506\UGFLEXLM\lmutil` | `lmutil` in another location or NX version |
| `-InputFile` | none | Parse a saved `lmstat -a` output instead of querying the server. Prints the report but **saves nothing**, so it is safe for testing |

## Files

* `CheckLicenses.bat`: the double-click launcher
* `CheckLicenses.ps1`: runs `lmutil`, builds and saves the report
* `output\license_status_latest.txt`, `output\license_status_raw.txt`: results
  (the `output\` folder is git-ignored)
