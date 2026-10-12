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

from lib.layers import move_to_layer  # noqa: E402
from lib.vendor_part import create_vendor_part  # noqa: E402

# ---- Hardcoded debug values (edit these) ----
ID = "vendor_2"
NAME = "vendor_description_2"
MANUFACTURER = "vendor_name_2"
PART_CLASS = "Class III"

# ---- Which tests to run (toggle these) ----
RUN_CREATE_VENDOR_PART = False
RUN_MOVE_TO_LAYER = True
TARGET_LAYER = 70          # move_to_layer: moves all bodies in the work part


def _test_create_vendor_part(lw):
    lw.WriteLine("debug.py: create_vendor_part")
    lw.WriteLine("  ID           : {0}".format(ID))
    lw.WriteLine("  Name         : {0}".format(NAME))
    lw.WriteLine("  Manufacturer : {0}".format(MANUFACTURER))
    lw.WriteLine("  Part Class   : {0}".format(PART_CLASS))
    try:
        part = create_vendor_part(ID, NAME, MANUFACTURER, PART_CLASS, lw=lw)
    except Exception as ex:
        lw.WriteLine("FAILED: {0}".format(ex))
        raise
    lw.WriteLine("Created: {0}".format(part.Leaf))


def _test_move_to_layer(lw):
    part = NXOpen.Session.GetSession().Parts.Work
    lw.WriteLine("debug.py: move_to_layer")
    lw.WriteLine("  Work part : {0}".format(part.Leaf))
    lw.WriteLine("  Bodies    : {0}".format(len(list(part.Bodies))))
    lw.WriteLine("  Layer     : {0}".format(TARGET_LAYER))
    try:
        moved = move_to_layer(TARGET_LAYER, part=part)
    except Exception as ex:
        lw.WriteLine("FAILED: {0}".format(ex))
        raise
    lw.WriteLine("Moved {0} object(s) to layer {1}".format(moved, TARGET_LAYER))


def main(args):
    lw = NXOpen.Session.GetSession().ListingWindow
    lw.Open()
    lw.WriteLine("=" * 60)
    if RUN_CREATE_VENDOR_PART:
        _test_create_vendor_part(lw)
        lw.WriteLine("-" * 60)
    if RUN_MOVE_TO_LAYER:
        _test_move_to_layer(lw)
    lw.WriteLine("=" * 60)


if __name__ == '__main__':
    main(sys.argv[1:])
