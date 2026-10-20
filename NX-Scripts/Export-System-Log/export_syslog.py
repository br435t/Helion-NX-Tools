# NX 2506
# Author:  br435t
# Created: 2026-10-19
# Exports the NX system log (syslog) to a text file.
#
# Run via File -> Execute -> NX Open... in any NX session. Copies the running
# session's system log (Session.LogFile.FileName, the same file as Help -> Log
# File) to <repo>/output/nx_syslog_<yyyy-mm-dd_HHMMSS>.txt, and prints the source
# and destination paths to the Listing Window. The output folder is git-ignored.
#
# The log is copied as it is right now: lines NX has not flushed to disk yet may be
# missing, and anything logged after the copy is not included. Run it again to get
# a fresh copy; each run writes a new timestamped file.
import os
import shutil
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))


def _find_repo_root():
    """Walk up from this script to the repo root (the dir holding lib/)."""
    d = _HERE
    for _ in range(6):
        if os.path.isfile(os.path.join(d, "lib", "__init__.py")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    raise RuntimeError("Could not find the repo root (folder containing lib/)")


import NXOpen  # noqa: E402


def main(args):
    lw = NXOpen.Session.GetSession().ListingWindow
    lw.Open()

    source = NXOpen.Session.GetSession().LogFile.FileName
    if not source or not os.path.isfile(source):
        lw.WriteLine("NX system log not found (LogFile.FileName = {0!r}).".format(source))
        return

    out_dir = os.path.join(_find_repo_root(), "output")
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)
    dest = os.path.join(out_dir, "nx_syslog_{0}.txt".format(time.strftime("%Y-%m-%d_%H%M%S")))

    try:
        shutil.copyfile(source, dest)
    except (IOError, OSError) as ex:
        lw.WriteLine("Could not copy the system log: {0}".format(ex))
        lw.WriteLine("  from: {0}".format(source))
        return

    lw.WriteLine("Exported NX system log ({0:,} bytes)".format(os.path.getsize(dest)))
    lw.WriteLine("  from: {0}".format(source))
    lw.WriteLine("    to: {0}".format(dest))


if __name__ == '__main__':
    main(None)
