"""McMaster-Carr data: run the vendored scraper and massage its output."""
import json
import os
import subprocess

from lib.paths import ROOT

# Vendored McMaster scraper (under lib/scraper) + output dir.
SCRAPER_SCRIPT = os.path.join(ROOT, "lib", "scraper", "mcmaster_scraper.py")
MCMASTER_OUT = r"C:\TEMP\MCMASTER"


def scraper_python():
    """External Python that has selenium installed (see lib/scraper/VENDORED.md).

    Preference order (so it works even when NX didn't inherit the env var):
      1. MCMASTER_SCRAPER_PYTHON environment variable
      2. the repo-root venv (<root>\\.venv\\Scripts\\python.exe)
      3. "python" on PATH

    The env var is skipped when it points at a full path that no longer
    exists (e.g. a stale value left over from a moved repo) so we fall through
    to the repo-root .venv instead of hard-aborting. A bare command name
    (no directory component, e.g. just "python") is trusted as-is since it is
    resolved on PATH, not on disk.
    """
    env = os.environ.get("MCMASTER_SCRAPER_PYTHON")
    if env:
        has_dir = bool(os.path.dirname(env))
        if not has_dir or os.path.exists(env):
            return env
        # else: stale/broken path -> ignore and fall through
    venv_py = os.path.join(ROOT, ".venv", "Scripts", "python.exe")
    if os.path.exists(venv_py):
        return venv_py
    return "python"


def run_scraper(sub_args, timeout=300):
    cmd = [scraper_python(), SCRAPER_SCRIPT] + sub_args
    return subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        universal_newlines=True, timeout=timeout)


def cad_failure_reason(proc):
    """Human-readable reason a `cad ... --json` run failed.

    With --json the scraper reports its own errors ("no CAD options found",
    "no 'parasolid' (no threads) option for this part", "CAD control did not
    render ...") as JSON on *stdout* and leaves stderr empty, so read stdout
    first and only fall back to stderr / the bare exit code.
    """
    try:
        message = (json.loads(proc.stdout) or {}).get("error")
    except ValueError:
        message = None
    if message:
        return message
    stderr = (proc.stderr or "").strip()
    if stderr:
        return stderr
    return "CAD download exited {0}".format(proc.returncode)


def fetch_mcmaster(part_no, out_dir=MCMASTER_OUT, log=None):
    """Scrape property data (JSON) and download the no-threads Parasolid CAD.

    Runs the vendored scraper in an external interpreter as a subprocess:
      1. `scrape <pn> --out <dir>`  -> writes <dir>/<pn>.json
      2. `cad <pn> --out <dir> --json` -> downloads the default 3-D Parasolid,
         no-threads *.X_T into <dir>

    Returns a dict:
      {"data": <scraped dict or None>, "json_file": path or None,
       "cad_file": path or None, "error": <scrape error or None>,
       "cad_error": <CAD error or None>}
    `error` means the JSON (and thus the description) is unavailable;
    `cad_error` means no CAD model was downloaded. Both abort creation in
    main() — see step 2b. Never raises.
    """
    result = {"data": None, "json_file": None, "cad_file": None,
              "error": None, "cad_error": None}  # type: dict
    _log = log or (lambda m: None)
    _log("  running lib/scraper/mcmaster_scraper.py ({0})".format(scraper_python()))
    try:
        os.makedirs(out_dir, exist_ok=True)
    except OSError as ex:
        result["error"] = "cannot create {0}: {1}".format(out_dir, ex)
        return result

    # 1. Scrape structured data to <out_dir>/<part_no>.json
    _log("  > scrape {0} --out {1}  (opens Edge; may take a moment)".format(
        part_no, out_dir))
    try:
        proc = run_scraper(["scrape", part_no, "--out", out_dir])
    except (OSError, subprocess.SubprocessError) as ex:
        result["error"] = "failed to run scraper: {0}".format(ex)
        return result
    if proc.returncode != 0:
        result["error"] = "scrape exited {0}: {1}".format(
            proc.returncode, (proc.stderr or "").strip())
        return result

    json_file = os.path.join(out_dir, part_no + ".json")
    if not os.path.exists(json_file):
        result["error"] = "scrape produced no JSON at {0}".format(json_file)
        return result
    try:
        with open(json_file, encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, ValueError) as ex:
        result["error"] = "cannot read scraped JSON: {0}".format(ex)
        return result
    result["json_file"] = json_file
    result["data"] = data
    if data.get("error"):
        result["error"] = "scrape error: {0}".format(data["error"])
        return result

    # 2. Download the CAD (default = 3-D Parasolid, no threads, *.X_T)
    _log("  > cad {0} --out {1}  (downloading no-threads Parasolid)".format(
        part_no, out_dir))
    try:
        cad_proc = run_scraper(["cad", part_no, "--out", out_dir, "--json"])
    except (OSError, subprocess.SubprocessError) as ex:
        result["cad_error"] = "failed to run CAD download: {0}".format(ex)
        return result
    if cad_proc.returncode == 0:
        try:
            result["cad_file"] = json.loads(cad_proc.stdout).get("file")
        except ValueError:
            result["cad_error"] = "could not parse CAD output"
        if not result["cad_error"] and not result["cad_file"]:
            result["cad_error"] = "CAD download reported no file"
    else:
        result["cad_error"] = cad_failure_reason(cad_proc)
    return result


def build_description(data):
    """part_desc = title_primary + title_secondary, concatenated and UPPERCASED."""
    primary = (data.get("title_primary") or "").strip()
    secondary = (data.get("title_secondary") or "").strip()
    return " ".join(p for p in (primary, secondary) if p).upper()


def make_filename_safe(name):
    """Sanitize a part name so NX can derive a valid part filename from it.

    In Teamcenter managed mode NX derives the new part's filename from the part
    name, and Windows filenames cannot contain  < > : " / \\ | ? *  -- but
    McMaster titles routinely use / and " (e.g. '1/4"-20'). Applied to the part
    NAME only ('"' -> 'IN', '/' -> '-') as a precaution; the full, unmodified
    text is not preserved on the part (DB_PART_DESC is no longer set).

    Note: the "The new filename is not a valid file specification" error chased
    during development turned out to be a duplicate item-id collision (operation
    failure 940519), not illegal characters -- see find_item_revision_spec().
    """
    name = name.replace('"', 'IN').replace('/', '-').replace('\\', '-')
    for bad in '<>:|?*':
        name = name.replace(bad, '')
    return " ".join(name.split())  # collapse whitespace, trim ends
