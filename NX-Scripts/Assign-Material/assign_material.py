# NX 2506
# Author:  br435t
# Created: 2026-10-23
# Assigns one material to bodies YOU select in the CURRENT part (the work part).
#
# Run via File -> Execute -> NX Open... with a part open.
#
# 1. Select the bodies in the graphics window (click bodies, then OK). Only solid bodies of the
#    current part can be selected. They get the material EVEN IF they already have one, which is
#    replaced; the next dialog says how many.
# 2. A dialog lists the Helion material library (same list-with-search dialog as
#    Color-By-Material/assign_and_color_materials.py): type part of a name, press Enter to filter,
#    select a material, OK. The selected bodies are highlighted while it is open.
#
# Cancelling either step changes nothing. After assigning, the bodies are colored (and given the
# translucency) from the material's row in Materials/NX_Materials.csv; a material with no color there
# leaves the body color alone. Last, the part's mass properties are updated (Analysis > Mass
# Properties > Update Now) so the weight uses the new material. All of it is one undo step and is NOT saved. See README.md in this folder, and lib/part_materials.py for the
# implementation.
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))


def _find_repo_root():
    """Walk up from this script to the repo root (the dir holding lib/) and
    put it on sys.path so `import lib...` works when NX runs the script."""
    d = _HERE
    for _ in range(6):
        if os.path.isfile(os.path.join(d, "lib", "__init__.py")):
            if d not in sys.path:
                sys.path.insert(0, d)
            return d
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    raise RuntimeError("Could not find the repo root (folder containing lib/)")


REPO_ROOT = _find_repo_root()

import NXOpen  # noqa: E402
from lib.part_materials import assign_material_to_part, pick_bodies  # noqa: E402

# The material picker dialog sits next to this script.
_DIALOG = os.path.join(_HERE, "ASSIGN_MATERIAL_PART_dialog.dlx")


def main(args):
    session = NXOpen.Session.GetSession()
    lw = session.ListingWindow
    lw.Open()
    part = session.Parts.Work
    if part is None:
        lw.WriteLine("No work part. Open a part first.")
        return
    if not os.path.isfile(_DIALOG):
        lw.WriteLine("Dialog file not found: {0}".format(_DIALOG))
        return

    bodies, rejected, status = pick_bodies(session, part)
    if status == "cancelled":
        lw.WriteLine("Selection cancelled. Nothing was changed.")
        return
    for line in rejected:
        lw.WriteLine("Skipped (not usable): {0}".format(line))
    if status == "empty":
        lw.WriteLine("No solid bodies selected. Nothing was changed.")
        return
    assign_material_to_part(session, part, _DIALOG, bodies)


if __name__ == '__main__':
    main(sys.argv[1:])
