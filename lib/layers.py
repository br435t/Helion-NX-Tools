"""Layer helpers (Format > Move to Layer)."""
import NXOpen
import NXOpen.Layer


def move_to_layer(layer, objects=None, part=None):
    """Move displayable objects to `layer` (1-256).

    Based on example_journals/journal_change_layer.py
    (Layers.MoveDisplayableObjects). `objects` is an iterable of
    NXOpen.DisplayableObject; when omitted, every body in the part is moved.
    `part` defaults to the current work part.

    Returns the number of objects moved (0 if there was nothing to move).
    """
    if not 1 <= layer <= 256:
        raise ValueError("layer must be 1-256, got {0}".format(layer))
    if part is None:
        part = NXOpen.Session.GetSession().Parts.Work
    if objects is None:
        objects = list(part.Bodies)
    objects = list(objects)
    if not objects:
        return 0
    part.Layers.MoveDisplayableObjects(layer, objects)
    return len(objects)
