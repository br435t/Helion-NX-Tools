"""Color the bodies of the displayed assembly by NX physical material.

Shared implementation behind NX-Scripts/Color-By-Material/*. Bodies with no
material get NO_MATERIAL_COLOR. Other styles come from
Materials/NX_Materials.csv: the "color" column (hex code, or NX color ID 1-216) and the "Transparency"
column (0 = opaque .. 100 = fully clear). See that folder's README for behavior,
caveats and the Listing Window output.
"""
import csv
import os

import NXOpen

from lib.assemblies import get_bodies, get_body_material, walk_components
from lib.colors import clear_component_color_override, color_number_from, set_body_color

# Bodies with no material assigned get this color (set to None to leave them alone).
NO_MATERIAL_COLOR = "#ff00ff"

MATERIALS_CSV = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "Materials", "NX_Materials.csv")


def _load_material_styles():
    """{lower-cased material name: (hex or None, translucency or None)} for CSV
    rows that have a "color" and/or a "Transparency" value. Column names are
    matched case-insensitively. A bad Transparency value is ignored."""
    styles = {}
    with open(MATERIALS_CSV, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            row = {(k or "").strip().lower(): (v or "").strip() for k, v in row.items()}
            hex_code = row.get("color") or None
            translucency = None
            raw = row.get("transparency", "")
            if raw:
                try:
                    translucency = max(0, min(100, int(round(float(raw)))))
                except ValueError:
                    translucency = None
            if hex_code or translucency is not None:
                styles[row["name"].lower()] = (hex_code, translucency)
    return styles


_bad_colors = set()      # color cells that were neither hex nor an NX ID (reported once)


def _color_number(value, part):
    """NX color number for a hex code or NX color ID, or None (blank or invalid;
    invalid values are remembered and reported at the end)."""
    try:
        return color_number_from(value, part)
    except ValueError:
        _bad_colors.add(value)
        return None


def _report_bad_colors(lw):
    if _bad_colors:
        lw.WriteLine("")
        lw.WriteLine("Ignored color values that are neither a hex code nor an NX color ID (1-216):")
        for value in sorted(_bad_colors):
            lw.WriteLine("  {0!r}".format(value))


def _resolve_style(material, material_styles):
    """(style, label) for a body's material name. style is (hex, translucency) or
    None when the body should be left alone; label is what the listing shows."""
    if material:
        return material_styles.get(material.lower()), material
    if NO_MATERIAL_COLOR:
        return (NO_MATERIAL_COLOR, None), "(no material)"
    return None, "(none)"


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
    _bad_colors.clear()

    display_part = session.Parts.Display
    if display_part is None:
        lw.WriteLine("No displayed part.")
        return

    material_styles = _load_material_styles()
    lw.WriteLine("{0} materials have a color and/or transparency in {1}".format(
        len(material_styles), MATERIALS_CSV))

    # One entry per distinct part: first component using it, and how many
    # instances there are.
    parts = {}           # part full path -> [part, first component, instances]
    # The displayed (active) part itself comes first: its own bodies count too, not
    # just those of its child components. It has no component (None) and is already
    # the work part, so nothing needs switching for it.
    parts[display_part.FullPath] = [display_part, None, 1]
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
    lw.WriteLine("Bodies changed (part / body -> material, NX color, transparency):")
    if NO_MATERIAL_COLOR:
        lw.WriteLine("(bodies with no material get {0})".format(NO_MATERIAL_COLOR))

    n_bodies = 0
    n_parts = 0
    unchanged = {}       # material (or "(none)") -> count
    skipped = []         # (part, reason) -- parts that could not be changed
    read_only = []       # part names that were changed but are read-only
    for proto, comp, instances in parts.values():
        # (palette number or None, translucency or None) -> [(body, material)]
        by_style = {}
        for body in proto.Bodies:
            style, material = _resolve_style(get_body_material(body), material_styles)
            if style is None:
                unchanged[material] = unchanged.get(material, 0) + 1
                continue
            hex_code, translucency = style
            number = _color_number(hex_code, display_part)
            by_style.setdefault((number, translucency), []).append((body, material))
        if not by_style:
            continue
        is_read_only = proto.IsReadOnly

        try:
            if comp is not None:
                session.Parts.SetWorkComponent(comp)
            for (number, translucency), items in by_style.items():
                set_body_color([b for b, _m in items], number, translucency)
        except Exception as ex:
            skipped.append((proto.Leaf, "could not make it the work part: {0}".format(ex)))
            continue
        finally:
            session.Parts.SetWork(display_part)

        n_parts += 1
        if is_read_only:
            read_only.append(proto.Leaf)
        for (number, translucency), items in by_style.items():
            for body, material in items:
                n_bodies += 1
                detail = []
                if number is not None:
                    detail.append("NX color {0}".format(number))
                if translucency is not None:
                    detail.append("transparency {0}".format(translucency))
                lw.WriteLine("  {0}{1} / {2} -> {3}, {4}{5}".format(
                    proto.Leaf, " (active part)" if comp is None else "",
                    _body_name(body), material, ", ".join(detail),
                    "  (used x{0})".format(instances) if instances > 1 else ""))

    lw.WriteLine("")
    lw.WriteLine("Changed {0} bodies in {1} parts (modified, NOT saved).".format(
        n_bodies, n_parts))
    lw.WriteLine("If a body still looks unchanged, it may carry a body-level override.")
    if read_only:
        lw.WriteLine("Read-only parts (changed in this session, cannot be saved as-is):")
        for name in read_only:
            lw.WriteLine("  {0}".format(name))
    if skipped:
        lw.WriteLine("Skipped parts:")
        for name, reason in skipped:
            lw.WriteLine("  {0}: {1}".format(name, reason))
    if unchanged:
        lw.WriteLine("Left unchanged (no color or transparency for material):")
        for name, n in sorted(unchanged.items()):
            lw.WriteLine("  {0:<32} x{1}".format(name, n))
    _report_bad_colors(lw)


def run_assembly_level():
    """Color every body in the displayed assembly by material using ASSEMBLY-LEVEL
    display overrides only: the override is set on each body occurrence in the
    displayed assembly. No component part is touched, nothing is made the work
    part, and read-only parts are not a concern. The one exception is the active
    part's OWN bodies, which are colored directly (they are not occurrences). Existing component-level color
    overrides are left as they are.
    """
    session = NXOpen.Session.GetSession()
    lw = session.ListingWindow
    lw.Open()
    _bad_colors.clear()

    display_part = session.Parts.Display
    if display_part is None:
        lw.WriteLine("No displayed part.")
        return

    material_styles = _load_material_styles()
    lw.WriteLine("{0} materials have a color and/or transparency in {1}".format(
        len(material_styles), MATERIALS_CSV))
    lw.WriteLine("Assembly-level overrides only: component parts are not modified.")
    if NO_MATERIAL_COLOR:
        lw.WriteLine("(bodies with no material get {0})".format(NO_MATERIAL_COLOR))
    lw.WriteLine("")
    lw.WriteLine("Bodies changed (component / body -> material, NX color, transparency):")

    # (palette number or None, translucency or None) -> [occurrence bodies]
    by_style = {}
    listing = {}         # (component, body, material, number, translucency) -> count
    unchanged = {}       # material (or "(none)") -> count

    def collect(label, bodies):
        for body in bodies:
            style, material = _resolve_style(get_body_material(body), material_styles)
            if style is None:
                unchanged[material] = unchanged.get(material, 0) + 1
                continue
            hex_code, translucency = style
            number = _color_number(hex_code, display_part)
            by_style.setdefault((number, translucency), []).append(body)
            key = (label, _body_name(body), material, number, translucency)
            listing[key] = listing.get(key, 0) + 1

    # The displayed (active) part's own bodies come first. These are the part's
    # real bodies (not occurrences), so this colors the active part itself; there
    # is no assembly to override them in.
    collect(display_part.Leaf + " (active part)", display_part.Bodies)
    for comp, _depth in walk_components():
        collect(comp.DisplayName, get_bodies(comp))

    n_bodies = 0
    for (number, translucency), bodies in by_style.items():
        n_bodies += set_body_color(bodies, number, translucency)

    # One line per distinct component/body, with a quantity when repeated.
    for (comp_name, body_name, material, number, translucency), n in listing.items():
        detail = []
        if number is not None:
            detail.append("NX color {0}".format(number))
        if translucency is not None:
            detail.append("transparency {0}".format(translucency))
        lw.WriteLine("  {0} / {1} -> {2}, {3}{4}".format(
            comp_name, body_name, material, ", ".join(detail),
            "  x{0}".format(n) if n > 1 else ""))

    lw.WriteLine("")
    lw.WriteLine("Changed {0} body occurrences (assembly-level, NOT saved).".format(n_bodies))
    lw.WriteLine("These overrides live in the assembly; the component parts are unchanged.")
    lw.WriteLine("Bodies owned by the active part itself are colored on that part.")
    if unchanged:
        lw.WriteLine("Left unchanged (no color or transparency for material):")
        for name, n in sorted(unchanged.items()):
            lw.WriteLine("  {0:<32} x{1}".format(name, n))
    _report_bad_colors(lw)
