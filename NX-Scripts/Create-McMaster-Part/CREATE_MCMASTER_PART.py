# NX 2506
# Journal created by br435t on Tue Jul 14 09:12:10 2026 Pacific Daylight Time
#
import json
import os
import subprocess
import sys
import NXOpen
import NXOpen.PDM
import NXOpen.BlockStyler

_HERE = os.path.dirname(os.path.abspath(__file__))


def _repo_root():
    """Walk up from this script to the repo root.

    This script lives a couple of levels down (NX-Scripts/Create-McMaster-Part/)
    while shared resources (Tools/, .venv) sit at the repo root. Find the root
    by looking for a marker (.git / .venv / Tools) walking upward.
    """
    d = _HERE
    for _ in range(6):
        if any(os.path.isdir(os.path.join(d, m)) for m in (".git", ".venv", "Tools")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return _HERE


_ROOT = _repo_root()

# Single-field BlockStyler dialogs (part-number and part-name prompts). These
# sit next to this script.
_PARTNO_DLX = os.path.join(_HERE, "CREATE_MCMASTER_PART_partno_dialog.dlx")
_PARTNAME_DLX = os.path.join(_HERE, "CREATE_MCMASTER_PART_partname_dialog.dlx")

# Vendored McMaster scraper (under Tools/ at the repo root) + output dir.
_SCRAPER_SCRIPT = os.path.join(_ROOT, "Tools", "scraper", "mcmaster_scraper.py")
MCMASTER_OUT = r"C:\TEMP\MCMASTER"

# Teamcenter destination folder for created COTS parts. The ":" prefix is TC
# folder syntax; using the real ":MCMASTER" folder (per the working recording
# journal_create_vendor_part.py) is what lets the manual-id Commit() succeed.
MCMASTER_TC_FOLDER = ":MCMASTER"


def prompt_string(dlx_path, block_id, default=None):
    """Show a single-field string BlockStyler dialog and return its value.

    Returns the stripped field value, or None if the user cancels. If `default`
    is given it is pre-filled into the field (editable by the user).

    BlockStyler dialogs require callback handlers to be registered (NX errors
    with "The Initialize callback is not registered" otherwise), and block
    values must be read inside the OK/Apply callback.
    """
    the_ui = NXOpen.UI.GetUI()
    dialog = the_ui.CreateDialog(dlx_path)
    captured = {}

    def initialize_cb():
        if default:
            props = dialog.GetBlockProperties(block_id)
            # Set both storages: a KeyIn field reads "Value", a Wide field
            # reads "WideValue". Best-effort — never block the dialog.
            for key in ("Value", "WideValue"):
                try:
                    props.SetString(key, default)
                except Exception:
                    pass

    def update_cb(block):
        return 0

    def apply_cb():
        props = dialog.GetBlockProperties(block_id)
        value = ""
        # Read WideValue first: for a Wide-presentation field that is the live
        # edited text, while "Value" may still hold the initialize prefill.
        for key in ("WideValue", "Value"):
            try:
                candidate = props.GetString(key)
            except Exception:
                candidate = ""
            if candidate:
                value = candidate
                break
        captured["value"] = value
        return 0

    def ok_cb():
        apply_cb()

    dialog.AddInitializeHandler(initialize_cb)
    dialog.AddUpdateHandler(update_cb)
    dialog.AddOkHandler(ok_cb)
    dialog.AddApplyHandler(apply_cb)

    try:
        response = dialog.Show()
        if response != NXOpen.Selection.Response.Ok:
            return None
        return (captured.get("value") or "").strip()
    finally:
        dialog.Dispose()


def _scraper_python():
    """External Python that has selenium installed (see Tools/scraper/VENDORED.md).

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
    venv_py = os.path.join(_ROOT, ".venv", "Scripts", "python.exe")
    if os.path.exists(venv_py):
        return venv_py
    return "python"


def _run_scraper(sub_args, timeout=300):
    cmd = [_scraper_python(), _SCRAPER_SCRIPT] + sub_args
    return subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        universal_newlines=True, timeout=timeout)


def _cad_failure_reason(proc):
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
    _log("  running Tools/scraper/mcmaster_scraper.py ({0})".format(_scraper_python()))
    try:
        os.makedirs(out_dir, exist_ok=True)
    except OSError as ex:
        result["error"] = "cannot create {0}: {1}".format(out_dir, ex)
        return result

    # 1. Scrape structured data to <out_dir>/<part_no>.json
    _log("  > scrape {0} --out {1}  (opens Edge; may take a moment)".format(
        part_no, out_dir))
    try:
        proc = _run_scraper(["scrape", part_no, "--out", out_dir])
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
        cad_proc = _run_scraper(["cad", part_no, "--out", out_dir, "--json"])
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
        result["cad_error"] = _cad_failure_reason(cad_proc)
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
    NAME only ('"' -> 'in', '/' -> '-') as a precaution; the full, unmodified
    text is preserved in the DB_PART_DESC attribute.

    Note: the "The new filename is not a valid file specification" error chased
    during development turned out to be a duplicate item-id collision (operation
    failure 940519), not illegal characters -- see item_exists_in_teamcenter().
    """
    name = name.replace('"', 'in').replace('/', '-').replace('\\', '-')
    for bad in '<>:|?*':
        name = name.replace(bad, '')
    return " ".join(name.split())  # collapse whitespace, trim ends


def import_parasolid(the_session, input_file, curves=True, surfaces=True, solids=True):
    """Import a Parasolid (*.x_t) file into the current work part.

    Mirrors the recorded File > Import > Parasolid flow (see import_Parasolid.py).
    """
    importer = the_session.DexManager.CreateParasolidImporter()
    try:
        importer.ObjectTypes.Curves = curves
        importer.ObjectTypes.Surfaces = surfaces
        importer.ObjectTypes.Solids = solids
        importer.SetMode(NXOpen.BaseImporter.Mode.NativeFileSystem)
        importer.InputFile = input_file
        importer.Commit()
    finally:
        importer.Destroy()


# Revision rules used to resolve an item id when checking for existence.
# An empty rule does NOT resolve existing parts here (verified via
# check_part_exists.py); "Latest Working" catches unreleased parts and
# "Any Status; Working" catches any status. If any rule resolves the id, the
# part exists. Extend this list if a part is known to exist but isn't detected.
_TC_EXISTENCE_REVISION_RULES = ("Latest Working", "Any Status; Working")


def item_exists_in_teamcenter(the_session, item_id, log=None):
    """Best-effort check whether an item id already exists in Teamcenter.

    Uses PdmSession.GetConfiguredRevisionOfItems across a few revision rules
    (see _TC_EXISTENCE_REVISION_RULES). Returns True as soon as one rule
    resolves a revision for the id. Any other outcome -- id not found under any
    rule, or an API error -- returns False so creation proceeds; a genuine
    duplicate that slips through is then caught at Commit() (operation-failure
    code 940519) and reported via _dump_pdm_errors(). Never raises.
    """
    _log = log or (lambda m: None)
    try:
        pdm = the_session.PdmSession
        for rule in _TC_EXISTENCE_REVISION_RULES:
            query = NXOpen.PDM.PdmSession.GetConfiguredRevisionInput()
            query.ItemId = item_id
            query.RevisionRuleName = rule
            _errors, results = pdm.GetConfiguredRevisionOfItems([query])
            for res in (results or []):
                spec = (res.ItemRevisionCliSpec or "").strip()
                if not res.HasFailed and spec:
                    _log("  Teamcenter already has {0} (revision {1}, "
                         "rule '{2}').".format(item_id, spec, rule))
                    return True
        return False
    except Exception as ex:
        _log("  existence pre-check inconclusive ({0}); relying on "
             "commit-time validation.".format(ex))
        return False


def _dump_pdm_errors(builder, lw, label):
    """Print the PDM builder's error/warning messages to the Listing Window.

    The generic "not a valid file specification" NXException hides the real
    per-object failure; ErrorMessageHandler.GetErrorMessages() and
    GetOperationFailures() carry the specifics. Best-effort — never raises.
    """
    try:
        handler = builder.GetErrorMessageHandler(True)
        try:
            errs = list(handler.GetErrorMessages() or [])
            warns = list(handler.GetWarningMessages() or [])
        finally:
            handler.Dispose()
        for m in errs:
            lw.WriteLine("  [{0}] ERROR:   {1}".format(label, m))
        for m in warns:
            lw.WriteLine("  [{0}] warning: {1}".format(label, m))
        if not errs and not warns:
            lw.WriteLine("  [{0}] (no PDM messages)".format(label))
    except Exception as ex:
        lw.WriteLine("  [{0}] could not read PDM messages: {1}".format(label, ex))
    # Structured operation-failure list (NXOpen.ErrorInfo: ErrorCode +
    # Description + ErrorObjectDescription). This is the reliable channel --
    # GetErrorMessages() tends to return NULL for these PDM builders.
    try:
        failures = builder.GetOperationFailures()
        try:
            count = failures.Length
            for i in range(count):
                info = failures.GetErrorInfo(i)
                try:
                    try:
                        code = info.ErrorCode
                    except Exception:
                        code = "?"
                    try:
                        desc = info.Description
                    except Exception:
                        desc = "?"
                    try:
                        obj = info.ErrorObjectDescription
                    except Exception:
                        obj = ""
                    lw.WriteLine("  [{0}] failure[{1}]: code={2} | {3}{4}".format(
                        label, i, code, desc,
                        (" | object: " + obj) if obj else ""))
                finally:
                    info.Dispose()
        finally:
            failures.Dispose()
    except Exception as ex:
        lw.WriteLine("  [{0}] could not read operation failures: {1}".format(
            label, ex))


def main(args) :

    theSession  = NXOpen.Session.GetSession() #type: NXOpen.Session
    workPart = theSession.Parts.Work
    displayPart = theSession.Parts.Display
    lw = theSession.ListingWindow
    lw.Open()
    lw.WriteLine("=" * 60)
    lw.WriteLine("Running CREATE_MCMASTER_PART.py (McMaster -> Teamcenter COTS part)")
    lw.WriteLine("=" * 60)

    # --- 1. Ask for the McMaster part number ---
    entered_pn = prompt_string(_PARTNO_DLX, "partNo")
    if entered_pn is None:
        lw.WriteLine("Cancelled: part number dialog dismissed.")
        return
    if not entered_pn:
        lw.WriteLine("Cancelled: no part number entered.")
        return

    # --- 1b. Abort early if this part already exists in Teamcenter ---
    # COTS item ids are the vendor part number (DB_PART_NO). Re-creating an
    # existing id fails at Commit() with the opaque "The new filename is not a
    # valid file specification"; catch it up front (before the scrape) instead.
    lw.WriteLine("Checking Teamcenter for existing part {0} ...".format(entered_pn))
    if item_exists_in_teamcenter(theSession, entered_pn, log=lw.WriteLine):
        NXOpen.UI.GetUI().NXMessageBox.Show(
            "Part Already Exists",
            NXOpen.NXMessageBox.DialogType.Warning,
            "Part {0} already exists in Teamcenter.\n\n"
            "Creation was cancelled to avoid a duplicate item.".format(entered_pn))
        lw.WriteLine("Aborted: {0} already exists in Teamcenter.".format(entered_pn))
        return

    # --- 2. Scrape JSON + download the no-threads Parasolid CAD ---
    # Modal notice so the user sees what's happening before the scraper runs
    # (it freezes NX's UI while Edge runs, so Listing Window text won't repaint
    # until afterward). Blocks until the user clicks OK.
    NXOpen.UI.GetUI().NXMessageBox.Show(
        "McMaster Scraper",
        NXOpen.NXMessageBox.DialogType.Information,
        "Starting the McMaster scraper for part {0}.\n\n"
        "This opens Microsoft Edge in the background and may take up to a "
        "minute per step (scrape, then CAD download).\n\n"
        "Click OK to continue.".format(entered_pn))
    lw.WriteLine("Fetching McMaster data for {0} -> {1} ...".format(
        entered_pn, MCMASTER_OUT))
    fetched = fetch_mcmaster(entered_pn, log=lw.WriteLine)
    if fetched["error"]:
        lw.WriteLine("Aborted: {0}".format(fetched["error"]))
        return
    data = fetched["data"]
    if fetched.get("json_file"):
        lw.WriteLine("  JSON: {0}".format(fetched["json_file"]))

    # --- 2b. No CAD -> abort before anything is created ---
    # The point of this tool is a COTS part WITH geometry. Creating the
    # Teamcenter item first and only then discovering there is no CAD would
    # leave an empty BE9_COTS item behind that has to be deleted by hand, so
    # a missing CAD file aborts the whole run here instead.
    cad_file = fetched.get("cad_file")
    if not cad_file or not os.path.exists(cad_file):
        reason = fetched.get("cad_error") or "no CAD file was downloaded"
        if cad_file and not os.path.exists(cad_file):
            reason = "downloaded CAD file is missing: {0}".format(cad_file)
        NXOpen.UI.GetUI().NXMessageBox.Show(
            "No CAD Available",
            NXOpen.NXMessageBox.DialogType.Error,
            "No CAD model could be downloaded for part {0}.\n\n"
            "{1}\n\n"
            "Nothing was created in Teamcenter. Check the part number on "
            "mcmaster.com — some items (e.g. raw stock or bulk goods) have "
            "no 3-D Parasolid model.".format(entered_pn, reason))
        lw.WriteLine("Aborted: no CAD for {0} ({1}).".format(entered_pn, reason))
        return
    lw.WriteLine("  CAD : {0}".format(cad_file))

    # --- 3. Derive attribute values ---
    part_no = (data.get("part_number") or entered_pn).strip()
    part_desc = build_description(data)          # title_primary + secondary, UPPER
    manufacturer = "MCMASTER"                    # hardcoded
    part_class = "Class III"                     # hardcoded
    lw.WriteLine("  Description: {0}".format(part_desc))

    # --- 4. Ask the user for the part name (DB_PART_NAME), prefilled with the
    #        description as an editable default ---
    part_name = prompt_string(_PARTNAME_DLX, "partName", default=part_desc)
    if part_name is None:
        lw.WriteLine("Cancelled: part name dialog dismissed.")
        return
    if not part_name:
        lw.WriteLine("Cancelled: no part name entered.")
        return

    # The part name becomes the part filename; strip illegal filename chars
    # (the full description is preserved in DB_PART_DESC).
    safe_name = make_filename_safe(part_name)
    if safe_name != part_name:
        lw.WriteLine("  Part name sanitized for filename: {0}".format(safe_name))
    part_name = safe_name
    lw.WriteLine("  Name       : {0}".format(part_name))

    lw.WriteLine("Creating COTS part {0} ...".format(part_no))

    # --- 5. Create the BE9_COTS item (File > New > Item) ---
    #
    # This block is a faithful transcription of the working recorded journal
    # (example_journals/journal_create_vendor_part.py). The exact call order
    # matters: NX derives the new part's on-disk filename during Commit(), and
    # deviating from the recording (single-pass creation, skipping the fileNew
    # re-sets or the extra CreateLogicalObjects) produces "The new filename is
    # not a valid file specification". Keep this in lockstep with the recording.
    def _configure_filenew(fn):
        fn.TemplateFileName = "@DB/model-plain-1-inch-template/A"
        fn.UseBlankTemplate = False
        fn.ApplicationName = "ModelTemplate"
        fn.Units = NXOpen.Part.Units.Inches
        fn.RelationType = "master"
        fn.UsesMasterModel = "No"                  # NOTE: string, not bool
        fn.TemplateType = NXOpen.FileNewTemplateType.Item
        fn.TemplatePresentationName = "Model"
        fn.ItemType = "BE9_Design,BE9_Electrical,BE9_COTS,BE9_Tooling"
        fn.Specialization = ""
        fn.SetCanCreateAltrep(False)

    fileNew = theSession.Parts.FileNew()
    _configure_filenew(fileNew)

    opBuilder = theSession.PdmSession.CreateCreateOperationBuilder(
        NXOpen.PDM.PartOperationBuilder.OperationType.Create)
    fileNew.SetPartOperationCreateBuilder(opBuilder)
    opBuilder.SetOperationSubType(
        NXOpen.PDM.PartOperationCreateBuilder.OperationSubType.FromTemplate)
    opBuilder.SetModelType("master")

    # Phase 1: create the logical objects as the dialog default type
    # (BE9_Design), set the destination folder, then re-assert the sub-type --
    # exactly as the recording does before switching to COTS.
    opBuilder.SetItemType("BE9_Design")
    opBuilder.CreateLogicalObjects()
    opBuilder.DefaultDestinationFolder = MCMASTER_TC_FOLDER
    opBuilder.SetOperationSubType(
        NXOpen.PDM.PartOperationCreateBuilder.OperationSubType.FromTemplate)

    # Phase 2: re-apply the fileNew settings, switch to BE9_COTS with no master,
    # and recreate the logical objects. The recording calls CreateLogicalObjects
    # a second time after grabbing the source objects; preserve that extra call.
    _configure_filenew(fileNew)
    opBuilder.SetAddMaster(False)
    opBuilder.SetItemType("BE9_COTS")
    logicalObjects = opBuilder.CreateLogicalObjects()
    sourceObjects = logicalObjects[0].GetUserAttributeSourceObjects()
    opBuilder.CreateLogicalObjects()

    # COTS parts are not auto-numbered: register an empty naming map (the part
    # number is set below as the DB_PART_NO attribute).
    namingMap = opBuilder.CreateAttributeTitleToNamingPatternMap([], [])
    errorList = opBuilder.AutoAssignAttributesWithNamingPattern(
        [logicalObjects[0]], [namingMap])
    errorList.Dispose()
    opBuilder.GetErrorMessageHandler(True)

    attrBuilder = theSession.AttributeManager.CreateAttributePropertiesBuilder(
        NXOpen.BasePart.Null, [],
        NXOpen.AttributePropertiesBuilder.OperationType.Create)
    attrBuilder.SetAttributeObjects([])
    attrBuilder.SetAttributeObjects([sourceObjects[0]])

    # Item-level attributes (category BE9_COTS). Property-set order (Title,
    # Category, StringValue) matches the recording.
    attrBuilder.Title = "DB_PART_NO"
    attrBuilder.Category = "BE9_COTS"
    attrBuilder.StringValue = part_no
    attrBuilder.CreateAttribute()

    attrBuilder.Title = "DB_PART_NAME"
    attrBuilder.StringValue = part_name
    attrBuilder.Category = "BE9_COTS"
    attrBuilder.CreateAttribute()

    attrBuilder.Title = "DB_PART_DESC"
    attrBuilder.Category = "BE9_COTS"
    attrBuilder.StringValue = part_desc
    attrBuilder.CreateAttribute()

    # Revision-level attributes (category BE9_COTSRevision).
    attrBuilder.Title = "HE_Manufacturer"
    attrBuilder.Category = "BE9_COTSRevision"
    attrBuilder.StringValue = manufacturer
    attrBuilder.CreateAttribute()

    attrBuilder.Title = "Part Class"
    attrBuilder.StringValue = part_class
    attrBuilder.Category = "BE9_COTSRevision"
    attrBuilder.CreateAttribute()

    # Finalize and commit. The recording re-applies the fileNew settings once
    # more here, right before validating and committing.
    _configure_filenew(fileNew)
    fileNew.MasterFileName = ""
    fileNew.MakeDisplayedPart = True
    fileNew.DisplayPartOption = NXOpen.DisplayPartOption.AllowAdditional
    opBuilder.ValidateLogicalObjectsToCommit()
    _dump_pdm_errors(opBuilder, lw, "after Validate")
    opBuilder.CreateSpecificationsForLogicalObjects([logicalObjects[0]])
    _dump_pdm_errors(opBuilder, lw, "after CreateSpecs")
    try:
        fileNew.Commit()
    except Exception as commit_ex:
        lw.WriteLine("Commit() raised: {0}".format(commit_ex))
        _dump_pdm_errors(opBuilder, lw, "after Commit failure")
        raise

    workPart = theSession.Parts.Work
    displayPart = theSession.Parts.Display
    lw.WriteLine("Created COTS part: {0}".format(workPart.Leaf))

    fileNew.Destroy()
    attrBuilder.Destroy()

    # --- 6. Import the downloaded Parasolid geometry into the new part ---
    # cad_file is guaranteed present here: a missing CAD aborted the run in
    # step 2b, before the part was created.
    lw.WriteLine("Running Parasolid import (import_parasolid)")
    lw.WriteLine("  > {0}".format(cad_file))
    import_parasolid(theSession, cad_file)
    lw.WriteLine("  imported geometry into {0}.".format(workPart.Leaf))

    theSession.CleanUpFacetedFacesAndEdges()


if __name__ == '__main__':
    main(sys.argv[1:])
