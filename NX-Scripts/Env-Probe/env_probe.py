# NX 2506
# Author:  br435t
# Created: 2026-10-14
# Standalone probe: prints what NX sees when it runs a script, so a
# "Unable to append module directory path in PYTHONPATH" warning can be traced.
#
# Imports nothing from lib/, so it runs from ANY folder. Run it via
# File -> Execute -> NX Open... from (1) the repo location and then (2) a short
# simple folder such as C:\Temp, and compare the Listing Window output.
import os
import sys
import NXOpen


def _check_dir(path):
    return "ok" if os.path.isdir(path) else "MISSING"


def main(args):
    session = NXOpen.Session.GetSession()
    lw = session.ListingWindow
    lw.Open()
    here = os.path.dirname(os.path.abspath(__file__))

    lw.WriteLine("=" * 60)
    lw.WriteLine("env_probe.py")
    lw.WriteLine("=" * 60)
    lw.WriteLine("Script file   : {0}".format(os.path.abspath(__file__)))
    lw.WriteLine("Script folder : {0}".format(here))
    lw.WriteLine("  length      : {0} characters".format(len(here)))
    lw.WriteLine("  non-ASCII   : {0}".format(
        any(ord(c) > 127 for c in here)))
    lw.WriteLine("  has spaces  : {0}".format(" " in here))
    lw.WriteLine("  UNC/network : {0}".format(here.startswith("\\\\")))
    lw.WriteLine("  OneDrive    : {0}".format("onedrive" in here.lower()))
    lw.WriteLine("Python        : {0}".format(sys.version.split()[0]))
    lw.WriteLine("Executable    : {0}".format(sys.executable))
    lw.WriteLine("")

    lw.WriteLine("Environment (as NX sees it):")
    for name in ("UGII_BASE_DIR", "UGII_ROOT_DIR", "UGII_PYTHON_HOME",
                 "UGII_ENV_FILE", "UGII_CUSTOM_DIRECTORY_FILE",
                 "UGII_USER_DIR", "UGII_USER_PROFILE_DIR", "PYTHONHOME"):
        lw.WriteLine("  {0} = {1}".format(name, os.environ.get(name, "(not set)")))
    lw.WriteLine("")

    for name in ("UGII_PYTHONPATH", "PYTHONPATH"):
        value = os.environ.get(name)
        lw.WriteLine("{0}: {1}".format(
            name, "(not set)" if value is None else
            "{0} characters".format(len(value))))
        if value:
            for i, entry in enumerate(value.split(";"), 1):
                shown = entry if entry else "<empty>"
                status = "EMPTY" if not entry else _check_dir(entry)
                if entry.lower().endswith(".zip") and os.path.isfile(entry):
                    status = "ok"
                lw.WriteLine("  {0:2}. {1:<8} {2}".format(i, status, shown))
        lw.WriteLine("")

    lw.WriteLine("sys.path:")
    for i, entry in enumerate(sys.path, 1):
        status = _check_dir(entry)
        if entry.lower().endswith(".zip") and os.path.isfile(entry):
            status = "ok"
        lw.WriteLine("  {0:2}. {1:<8} {2}".format(i, status, entry))
    lw.WriteLine("")

    lib_dir = None
    d = here
    for _ in range(6):
        if os.path.isfile(os.path.join(d, "lib", "__init__.py")):
            lib_dir = d
            break
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    lw.WriteLine("Repo root (folder containing lib/): {0}".format(
        lib_dir if lib_dir else "NOT FOUND from this script's location"))
    lw.WriteLine("=" * 60)


if __name__ == '__main__':
    main(sys.argv[1:])
