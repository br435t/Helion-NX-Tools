# NX 2506
# Author:  br435t
# Created: 2026-10-27
# Exports every solid body to a local DXF AND to Teamcenter: one DXF dataset per solid
# body, named <partID>_<revision>_<bodyname>, under the part's item revision (recorded in
# example_journals/journal_export_dxf_TC.py). The local DXF files are still written to the repo's output
# folder. For each body of the WORK part: measure every face, take the largest flat face, save a view
# looking straight at it (zoomed to fit) called DXF_<BODYNAME>, export the body through that view with all
# edges shown. The Listing Window reports the result of both exports. Needs a part opened from Teamcenter.
# See README.md in this folder and lib/body_dxf.py for the implementation.
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
from lib.body_dxf import export_part_bodies, is_teamcenter_part  # noqa: E402


def main(args):
    session = NXOpen.Session.GetSession()
    lw = session.ListingWindow
    lw.Open()
    part = session.Parts.Work
    if part is None:
        lw.WriteLine("No work part. Open a part first.")
        return
    if session.Parts.Display is None or session.Parts.Display.Tag != part.Tag:
        lw.WriteLine("Make the part the displayed part first (the views are made in the graphics window).")
        return
    if not is_teamcenter_part(part):
        lw.WriteLine("'{0}' was not opened from Teamcenter, so there is no item revision to attach "
                     "datasets to. Open the part from Teamcenter first.".format(part.Leaf))
        return

    lw.WriteLine("Exporting DXF files for {0} (local files and Teamcenter datasets) ...".format(part.Leaf))
    result = export_part_bodies(session, part, log=lw.WriteLine, teamcenter=True)

    files, datasets = len(result["exported"]), len(result["datasets"])
    tried = files + len(result["failures"])
    lw.WriteLine("")
    lw.WriteLine("RESULT for {0}".format(part.Leaf))
    lw.WriteLine("Local DXF files: {0} of {1} written to {2}".format(files, tried, result["out_dir"]))
    lw.WriteLine("Teamcenter datasets: {0} of {1} created on {2}".format(datasets, files, part.Leaf))
    for name, dataset in result["datasets"]:
        lw.WriteLine("  dataset {0}  (body {1})".format(dataset, name))
    for name, why in result["dataset_failures"]:
        lw.WriteLine("  Teamcenter FAILED for {0}: {1}".format(name, why))
    for name, why in result["skipped"]:
        lw.WriteLine("Skipped {0}: {1}".format(name, why))
    for name, why in result["failures"]:
        lw.WriteLine("Failed {0}: {1}".format(name, why))


if __name__ == '__main__':
    main(sys.argv[1:])
