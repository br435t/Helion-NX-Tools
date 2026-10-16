# NX 2506
# Walks the assembly tree of the displayed part and writes an indented list of
# every component to a text file.
#
# Run via File -> Execute -> NX Open... with an assembly displayed. Output goes
# to <part leaf name>_components.txt in the repo's output/ folder (git-ignored),
# and the path is echoed to the Listing Window.
#
# Each component line: indent by depth, DisplayName (instance name), the part it
# points at, and "[suppressed]" / "[not loaded]" flags where they apply. The
# bodies in that component are listed beneath it, one level deeper, as
# "- <body name> [solid|sheet] [blanked] material: <NX material>".
import os
import re
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
from lib.assemblies import get_bodies, get_body_material, walk_components  # noqa: E402


def _output_dir():
    out = os.path.join(REPO_ROOT, "output")
    if not os.path.isdir(out):
        os.makedirs(out)
    return out


def _part_label(comp):
    """Name of the part the component is an instance of, or '' if not loaded."""
    try:
        proto = comp.Prototype
        return proto.Leaf if proto is not None else ""
    except Exception:
        return ""


def _describe(comp, depth):
    """One output line for a component, plus the part name it points at."""
    flags = []
    part_name = _part_label(comp)
    if not part_name:
        flags.append("[not loaded]")
    try:
        if comp.IsSuppressed:
            flags.append("[suppressed]")
    except Exception:
        pass
    line = "{0}{1}  (part: {2}) {3}".format(
        "    " * (depth - 1), comp.DisplayName, part_name or "?", " ".join(flags))
    return line.rstrip(), part_name


def _describe_body(body, depth):
    try:
        name = body.Name or body.JournalIdentifier
    except Exception:
        name = "?"
    flags = ["[solid]" if body.IsSolidBody else "[sheet]"]
    try:
        if body.IsBlanked:
            flags.append("[blanked]")
    except Exception:
        pass
    flags.append("material: {0}".format(get_body_material(body) or "(none)"))
    return "{0}- {1} {2}".format("    " * depth, name, " ".join(flags))


def main():
    session = NXOpen.Session.GetSession()
    lw = session.ListingWindow
    lw.Open()

    part = session.Parts.Display
    if part is None:
        lw.WriteLine("No displayed part.")
        return

    lines = []
    counts = {}
    n_comps = 0
    n_bodies = 0
    for comp, depth in walk_components():
        line, part_name = _describe(comp, depth)
        lines.append(line)
        n_comps += 1
        counts[part_name] = counts.get(part_name, 0) + 1
        for body in get_bodies(comp):
            lines.append(_describe_body(body, depth))
            n_bodies += 1

    if not n_comps:
        lw.WriteLine("'{0}' has no components (piece part, or not fully loaded).".format(
            part.Leaf))
        return

    # Teamcenter leaf names look like "item/rev"; replace characters that are
    # illegal in a Windows filename.
    safe_name = re.sub(r'[\\/:*?"<>|]', "_", part.Leaf)
    out_path = os.path.join(_output_dir(), "{0}_components.txt".format(safe_name))

    with open(out_path, "w") as f:
        f.write("Assembly: {0}\n".format(part.FullPath))
        f.write("Components (excluding root): {0}   Bodies: {1}\n\n".format(
            n_comps, n_bodies))
        f.write("\n".join(lines) + "\n\n")
        f.write("Quantity by part:\n")
        for name in sorted(counts):
            f.write("  {0:<40} {1}\n".format(name or "?", counts[name]))

    lw.WriteLine("Wrote {0} components, {1} bodies to {2}".format(
        n_comps, n_bodies, out_path))


main()
