# NX 2506
# Debug launcher for lib.vendor_part.create_vendor_part.
#
# Run via File -> Execute -> NX Open... with an active Teamcenter (managed)
# session. Edit the hardcoded values below, then run.
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

from lib.vendor_part import create_vendor_part  # noqa: E402

# ---- Hardcoded debug values (edit these) ----
ID = "vendor_2"
NAME = "vendor_description_2"
MANUFACTURER = "vendor_name_2"
PART_CLASS = "Class III"


def main(args):
    lw = NXOpen.Session.GetSession().ListingWindow
    lw.Open()
    lw.WriteLine("=" * 60)
    lw.WriteLine("debug.py: create_vendor_part")
    lw.WriteLine("  ID           : {0}".format(ID))
    lw.WriteLine("  Name         : {0}".format(NAME))
    lw.WriteLine("  Manufacturer : {0}".format(MANUFACTURER))
    lw.WriteLine("  Part Class   : {0}".format(PART_CLASS))
    lw.WriteLine("=" * 60)

    try:
        part = create_vendor_part(ID, NAME, MANUFACTURER, PART_CLASS, lw=lw)
    except Exception as ex:
        lw.WriteLine("FAILED: {0}".format(ex))
        raise
    lw.WriteLine("Created: {0}".format(part.Leaf))


if __name__ == '__main__':
    main(sys.argv[1:])
