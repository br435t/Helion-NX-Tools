# NX 2506
# Author:  br435t
# Created: 2026-10-19
# Colors every body in the displayed assembly according to its NX physical
# material, using the "color" and "Transparency" columns of
# Materials/NX_Materials.csv.
#
# Run via File -> Execute -> NX Open... with an assembly displayed.
#
# ASSEMBLY-LEVEL variant: the color/transparency is set as a display override on
# each body occurrence in the displayed assembly. The component parts are NOT
# modified (nothing is made the work part, read-only parts do not matter), and
# existing component-level overrides are left as they are. Use color_by_material.py
# to change the parts themselves. See README.md in this folder, and
# lib/color_by_material.py (run_assembly_level) for the implementation.
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

from lib.color_by_material import run_assembly_level  # noqa: E402

run_assembly_level()
