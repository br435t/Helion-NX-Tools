"""Color the bodies of the displayed assembly by NX physical material.

Shared implementation behind NX-Scripts/Color-By-Material/*. Colors come from
the "color" column (hex) of Materials/NX_Materials.csv. See that folder's
README for behavior, caveats and the Listing Window output.
"""
import csv
import os

import NXOpen

from lib.assemblies import get_body_material, walk_components
from lib.colors import clear_component_color_override, nearest_color_number, set_body_color

MATERIALS_CSV = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "Materials", "NX_Materials.csv")


def _load_material_colors():
    """{lower-cased material name: hex} for CSV rows that have a color."""
    colors = {}
    with open(MATERIALS_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            hex_code = (row.get("color") or "").strip()
            if hex_code:
                colors[row["name"].strip().lower()] = hex_code
    return colors


def _body_name(body):
    try:
        return body.Name or body.JournalIdentifier
    except Exception:
        return "?"


def run(clear_overrides):
    """Color every body in the displayed assembly by material.

    clear_overrides: also clear the assembly-level color override on every
    component first (so part colors are visible).
    """
    session = NXOpen.Session.GetSession()
    lw = session.ListingWindow
    lw.Open()

    display_part = session.Parts.Display
    if display_part is None:
        lw.WriteLine("No displayed part.")
        return

    material_colors = _load_material_colors()
    lw.WriteLine("{0} materials have a color in {1}".format(
        len(material_colors), MATERIALS_CSV))

    # One entry per distinct part: first component using it, and how many
    # instances there are.
    parts = {}           # part full path -> [part, first component, instances]
    for comp, _depth in walk_components():
        try:
            proto = comp.Prototype
            if proto is None or comp.IsSuppressed:
                continue
            key = proto.FullPath
        except Exception:
            continue
        if key in parts:
            parts[key][2] += 1
        else:
            parts[key] = [proto, comp, 1]

    lw.WriteLine("{0} distinct parts in the assembly".format(len(parts)))
    if clear_overrides:
        n = clear_component_color_override([c for c, _d in walk_components()], display_part)
        lw.WriteLine("Cleared assembly color override on {0} components".format(n))
    lw.WriteLine("")
    lw.WriteLine("Bodies colored (part / body -> material, NX color):")

    n_bodies = 0
    n_parts = 0
    uncolored = {}       # material (or "(none)") -> count
    skipped = []         # (part, reason) -- parts that could not be colored
    read_only = []       # part names that were colored but are read-only
    for proto, comp, instances in parts.values():
        by_color = {}    # palette number -> [(body, material)]
        for body in proto.Bodies:
            material = get_body_material(body)
            hex_code = material_colors.get((material or "").lower())
            if hex_code is None:
                key = material or "(none)"
                uncolored[key] = uncolored.get(key, 0) + 1
                continue
            number, _rgb = nearest_color_number(hex_code, display_part)
            by_color.setdefault(number, []).append((body, material))
        if not by_color:
            continue
        is_read_only = proto.IsReadOnly

        try:
            session.Parts.SetWorkComponent(comp)
            for number, items in by_color.items():
                set_body_color([b for b, _m in items], number)
        except Exception as ex:
            skipped.append((proto.Leaf, "could not make it the work part: {0}".format(ex)))
            continue
        finally:
            session.Parts.SetWork(display_part)

        n_parts += 1
        if is_read_only:
            read_only.append(proto.Leaf)
        for number, items in by_color.items():
            for body, material in items:
                n_bodies += 1
                lw.WriteLine("  {0} / {1} -> {2}, NX color {3}{4}".format(
                    proto.Leaf, _body_name(body), material, number,
                    "  (used x{0})".format(instances) if instances > 1 else ""))

    lw.WriteLine("")
    lw.WriteLine("Colored {0} bodies in {1} parts (modified, NOT saved).".format(
        n_bodies, n_parts))
    lw.WriteLine("If a body still looks unchanged, it may carry a body-level override.")
    if read_only:
        lw.WriteLine("Read-only parts (colored in this session, cannot be saved as-is):")
        for name in read_only:
            lw.WriteLine("  {0}".format(name))
    if skipped:
        lw.WriteLine("Skipped parts:")
        for name, reason in skipped:
            lw.WriteLine("  {0}: {1}".format(name, reason))
    if uncolored:
        lw.WriteLine("Left unchanged (no color for material):")
        for name, n in sorted(uncolored.items()):
            lw.WriteLine("  {0:<32} x{1}".format(name, n))
