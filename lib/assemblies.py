"""Assembly tree helpers."""
import NXOpen


def walk_components(root=None, include_root=False):
    """Yield (component, depth) for every component below `root`, depth-first.

    `root` defaults to the root component of the displayed part. Depth is 1 for
    direct children of the root (0 for the root itself when include_root=True).
    Yields nothing for a piece part, or when the assembly is not fully loaded
    (RootComponent is None).
    """
    if root is None:
        part = NXOpen.Session.GetSession().Parts.Display
        root = part.ComponentAssembly.RootComponent if part is not None else None
    if root is None:
        return

    stack = [(root, 0)]
    while stack:
        comp, depth = stack.pop()
        if depth > 0 or include_root:
            yield comp, depth
        # Reversed so children come out in tree order from a LIFO stack.
        for child in reversed(comp.GetChildren()):
            stack.append((child, depth + 1))


def find_component(predicate, root=None):
    """Return the first component (depth-first) for which predicate(comp) is
    true, or None. E.g.:

        find_component(lambda c: c.DisplayName == "BRACKET")
        find_component(lambda c: c.Prototype.Leaf.startswith("1150201-500"))

    An exception raised by the predicate (e.g. Prototype on an unloaded
    component) counts as no match.
    """
    for comp, _depth in walk_components(root):
        try:
            if predicate(comp):
                return comp
        except Exception:
            continue
    return None


def get_bodies(component, solid_only=False, include_hidden=True):
    """Return the bodies of `component` as occurrences in the assembly context
    (so they can be used with the displayed part: blank, measure, move to layer).

    Walks the bodies of the component's prototype part and maps each through
    Component.FindOccurrence. Returns [] if the component is not loaded or is
    suppressed. Child components are NOT included; combine with
    walk_components to gather a whole subtree.

    solid_only:     keep only solid bodies (drop sheet bodies).
    include_hidden: when False, drop bodies that are blanked.
    """
    try:
        proto_part = component.Prototype
        if proto_part is None or component.IsSuppressed:
            return []
        proto_bodies = list(proto_part.Bodies)
    except Exception:
        return []

    bodies = []
    for proto in proto_bodies:
        if solid_only and not proto.IsSolidBody:
            continue
        try:
            occ = component.FindOccurrence(proto)
        except Exception:
            occ = None
        if occ is None:
            continue
        if not include_hidden and occ.IsBlanked:
            continue
        bodies.append(occ)
    return bodies


def get_body_material(body):
    """Return the name of the NX physical material assigned to `body`, or None.

    Materials are stored on the prototype body in its owning part, so an
    occurrence body (as returned by get_bodies) is mapped back to its prototype
    and the owning part's MaterialManager is asked. Returns None when no
    material is assigned or the lookup fails.
    """
    try:
        proto = body.Prototype if body.IsOccurrence else body
        material = proto.OwningPart.MaterialManager.PhysicalMaterials.AskMaterialOfObject(proto)
        return material.Name if material is not None else None
    except Exception:
        return None
