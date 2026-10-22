"""View helpers."""
import NXOpen


def fit_work_view(part=None):
    """Zoom the work view of `part` (default: the displayed part) to fit all the model geometry.

    Uses ModelingView.Fit(). Returns True if the view was fitted, False if it could not
    be (no part, or NX refused); never raises, so a zoom problem can never turn a
    finished operation into a failure.
    """
    try:
        if part is None:
            part = NXOpen.Session.GetSession().Parts.Display
        if part is None:
            return False
        part.ModelingViews.WorkView.Fit()
        return True
    except Exception:
        return False
