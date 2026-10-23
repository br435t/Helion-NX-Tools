"""Assign one library material to the bodies of a part that have none.

Used by NX-Scripts/Assign-Material. The material is picked in a BlockStyler dialog (the same
list-with-search dialog style as Color-By-Material's ASSIGN_MATERIAL_dialog.dlx).
"""
import NXOpen

from lib.assemblies import assign_material, get_body_material
from lib.color_by_material import load_material_libraries, load_material_names
from lib.nx_dialogs import choose_from_list


def _body_name(body):
    try:
        return body.Name or body.JournalIdentifier
    except Exception:
        return "?"


def _highlight(bodies):
    for b in bodies:
        try:
            b.Highlight()
        except Exception:
            pass


def _unhighlight(bodies):
    for b in bodies:
        try:
            b.Unhighlight()
        except Exception:
            pass


def assign_material_to_part(session, part, dialog_path):
    """Ask for a material and assign it to every body of `part` that has none.

    `part` must be the current work part (NX assigns materials in the work part's context).
    Bodies that already have a material are left alone. One dialog is shown; cancelling it, or
    pressing OK with nothing selected, changes nothing. The bodies that are about to receive
    the material are highlighted while the dialog is open.

    Everything done is a single undo step ("Assign Material to Part"); nothing is saved.
    Writes a report to the Listing Window and returns a dict:
        status    "assigned" | "nothing_to_do" | "cancelled" | "no_bodies" | "error"
        material  the chosen name (or None)
        assigned  [body names]   skipped [body names that already had a material]
        failures  [(body name, reason)]
    """
    lw = session.ListingWindow
    lw.Open()
    result = {"status": "error", "material": None, "assigned": [], "skipped": [], "failures": []}

    bodies = list(part.Bodies)
    if not bodies:
        lw.WriteLine("'{0}' has no bodies. Nothing to do.".format(part.Leaf))
        result["status"] = "no_bodies"
        return result

    missing = [b for b in bodies if get_body_material(b) is None]
    result["skipped"] = [_body_name(b) for b in bodies if b not in missing]
    if not missing:
        lw.WriteLine("All {0} bodies of '{1}' already have a material. Nothing to do.".format(
            len(bodies), part.Leaf))
        result["status"] = "nothing_to_do"
        return result

    names = load_material_names()
    libraries = load_material_libraries()
    heading = "{0}: {1} of {2} bodies have no material. Pick one for them:".format(
        part.Leaf, len(missing), len(bodies))

    _highlight(missing)
    try:
        chosen, _skip = choose_from_list(
            dialog_path, "materialList", names, heading=heading,
            heading_id="heading", search_id="searchBox",
            on_shown=lambda: _highlight(missing))
    except Exception as ex:
        lw.WriteLine("Could not show the material dialog: {0}".format(ex))
        return result
    finally:
        _unhighlight(missing)

    if not chosen:
        lw.WriteLine("No material chosen. Nothing was changed.")
        result["status"] = "cancelled"
        return result

    result["material"] = chosen
    if getattr(part, "IsReadOnly", False):
        lw.WriteLine("Note: '{0}' is read-only, so the assignment can be made in this session "
                     "but cannot be saved over the original.".format(part.Leaf))

    mark = session.SetUndoMark(NXOpen.Session.MarkVisibility.Visible, "Assign Material to Part")
    lib_files = libraries.get(chosen.lower(), ())
    for body in missing:
        ok, why = assign_material(part, body, chosen, lib_files)
        if ok:
            result["assigned"].append(_body_name(body))
        else:
            result["failures"].append((_body_name(body), why))

    if result["assigned"]:
        session.SetUndoMarkName(mark, "Assign Material to Part")
    else:
        try:
            session.UndoToMark(mark, None)       # nothing took: drop what loading the material may have added
            session.DeleteUndoMark(mark, None)
        except Exception:
            pass

    result["status"] = "assigned" if result["assigned"] else "error"
    lw.WriteLine("Material: {0}".format(chosen))
    lw.WriteLine("Assigned to {0} of {1} bodies in {2} (not saved):".format(
        len(result["assigned"]), len(missing), part.Leaf))
    for name in result["assigned"]:
        lw.WriteLine("  {0}".format(name))
    if result["skipped"]:
        lw.WriteLine("Left alone, already had a material: {0}".format(len(result["skipped"])))
    if result["failures"]:
        lw.WriteLine("Could not assign ({0}):".format(len(result["failures"])))
        for name, why in result["failures"]:
            lw.WriteLine("  {0}: {1}".format(name, why))
    return result
