# NX 2506
# Journal created by br435t on Tue Jul 14 09:12:10 2026 Pacific Daylight Time
#
# User-facing flow only. Every helper this script calls lives in lib/ at the
# repo root (lib/mcmaster.py, lib/teamcenter.py, lib/nx_dialogs.py).
import os
import sys
import NXOpen

_HERE = os.path.dirname(os.path.abspath(__file__))


def _add_repo_root_to_path():
    """Walk up from this script to the repo root (the dir holding lib/) and
    put it on sys.path so `import lib...` works when NX runs the script."""
    d = _HERE
    for _ in range(6):
        if os.path.isfile(os.path.join(d, "lib", "__init__.py")):
            if d not in sys.path:
                sys.path.insert(0, d)
            return
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent


_add_repo_root_to_path()

from lib.mcmaster import MCMASTER_OUT, build_description, fetch_mcmaster, make_filename_safe  # noqa: E402
from lib.nx_dialogs import ask_yes_no, prompt_string  # noqa: E402
from lib.teamcenter import MCMASTER_TC_FOLDER, import_parasolid, item_exists_in_teamcenter  # noqa: E402
from lib.vendor_part import create_vendor_part  # noqa: E402

# Single-field BlockStyler dialogs (part-number and part-name prompts). These
# sit next to this script.
_PARTNO_DLX = os.path.join(_HERE, "CREATE_MCMASTER_PART_partno_dialog.dlx")
_PARTNAME_DLX = os.path.join(_HERE, "CREATE_MCMASTER_PART_partname_dialog.dlx")


def main(args) :

    theSession  = NXOpen.Session.GetSession() #type: NXOpen.Session
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

    # --- 2b. No CAD -> ask the user whether to continue ---
    # Some items (raw stock, bulk goods, e.g. 5887K51) have no 3-D Parasolid
    # model. Creating the Teamcenter item without geometry leaves an empty
    # BE9_COTS item, so ask before going on; "No" aborts before anything is
    # created. "Yes" creates the part and skips the geometry import (step 6).
    cad_file = fetched.get("cad_file")
    if not cad_file or not os.path.exists(cad_file):
        reason = fetched.get("cad_error") or "no CAD file was downloaded"
        if cad_file and not os.path.exists(cad_file):
            reason = "downloaded CAD file is missing: {0}".format(cad_file)
        lw.WriteLine("No CAD for {0}: {1}".format(entered_pn, reason))
        if not ask_yes_no(
                "No CAD Available",
                "No CAD model could be downloaded for part {0}.\n\n"
                "{1}\n\n"
                "Create the part in Teamcenter WITHOUT geometry?\n\n"
                "Yes = create an empty part (no CAD imported)\n"
                "No  = cancel; nothing is created.".format(entered_pn, reason)):
            lw.WriteLine("Aborted: no CAD for {0}; user declined to create "
                         "an empty part.".format(entered_pn))
            return
        cad_file = None
        lw.WriteLine("  Continuing without CAD (empty part will be created).")
    else:
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
    # (the DB_PART_DESC attribute is no longer set).
    safe_name = make_filename_safe(part_name)
    if safe_name != part_name:
        lw.WriteLine("  Part name sanitized for filename: {0}".format(safe_name))
    part_name = safe_name
    lw.WriteLine("  Name       : {0}".format(part_name))

    # --- 5. Create the BE9_COTS item (File > New > Item) ---
    lw.WriteLine("Creating COTS part {0} ...".format(part_no))
    workPart = create_vendor_part(part_no, part_name, manufacturer, part_class,
                                  destination_folder=MCMASTER_TC_FOLDER, lw=lw)

    # --- 6. Import the downloaded Parasolid geometry into the new part ---
    # cad_file is None when the user chose to create the part without CAD
    # (step 2b); there is nothing to import in that case.
    if cad_file:
        lw.WriteLine("Running Parasolid import (import_parasolid)")
        lw.WriteLine("  > {0}".format(cad_file))
        import_parasolid(theSession, cad_file)
        lw.WriteLine("  imported geometry into {0}.".format(workPart.Leaf))
    else:
        lw.WriteLine("  skipped Parasolid import (no CAD).")

    theSession.CleanUpFacetedFacesAndEdges()


if __name__ == '__main__':
    main(sys.argv[1:])
