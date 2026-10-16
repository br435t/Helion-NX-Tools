"""Color helpers: hex codes -> NX palette indices, and body color assignment."""
import NXOpen
import NXOpen.Preferences

_palette_cache = {}


def hex_to_rgb(hex_code):
    """'#03fcad' (or '03fcad') -> (3, 252, 173)."""
    h = hex_code.strip().lstrip("#")
    if len(h) != 6:
        raise ValueError("expected a 6-digit hex color, got {0!r}".format(hex_code))
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _palette(part):
    """{color number 1-216: (r, g, b) on 0-255} for the part's NX palette."""
    if not _palette_cache:
        prefs = part.Preferences.ObjectPreferences
        for n in range(1, 217):
            c = prefs.ConvertColorNumberToRGBValue(n)
            rgb = (c.RedColor, c.GreenColor, c.BlueColor)
            _palette_cache[n] = rgb
        # Some NX builds return 0-1 floats instead of 0-255.
        if max(max(v) for v in _palette_cache.values()) <= 1.0:
            for n, rgb in _palette_cache.items():
                _palette_cache[n] = tuple(x * 255.0 for x in rgb)
    return _palette_cache


def nearest_color_number(hex_code, part=None):
    """Return (color_number, (r, g, b)) of the NX palette entry (1-216) closest
    to `hex_code`. The NX palette has only 216 colors, so most hex codes are
    approximated; the returned RGB is what will actually be shown."""
    if part is None:
        part = NXOpen.Session.GetSession().Parts.Display
    target = hex_to_rgb(hex_code)
    best = min(_palette(part).items(),
               key=lambda kv: sum((a - b) ** 2 for a, b in zip(kv[1], target)))
    return best[0], tuple(int(round(x)) for x in best[1])


def set_body_color(bodies, color_number):
    """Color `bodies` (occurrence or prototype bodies) with an NX color number,
    including all their faces. Returns the number of bodies colored."""
    bodies = list(bodies)
    if not bodies:
        return 0
    dm = NXOpen.Session.GetSession().DisplayManager.NewDisplayModification()
    try:
        dm.ApplyToAllFaces = True
        dm.NewColor = color_number
        dm.Apply(bodies)
    finally:
        dm.Dispose()
    return len(bodies)


def clear_component_color_override(components, part=None):
    """Remove the assembly-level color override from `components` so they show
    their part's own colors again (Edit > Properties > Color > "Specific color"
    unticked). Based on example_journals/remove_assebly_color_override.py.

    `part` is the part whose PropertiesManager is used; it defaults to the work
    part, which must be the assembly that owns the components. Returns the
    number of components processed.
    """
    components = list(components)
    if not components:
        return 0
    if part is None:
        part = NXOpen.Session.GetSession().Parts.Work
    builder = part.PropertiesManager.CreateAssembliesGeneralPropertiesBuilder(components)
    try:
        builder.SpecificColor = False
        builder.Commit()
    finally:
        builder.Destroy()
    return len(components)
