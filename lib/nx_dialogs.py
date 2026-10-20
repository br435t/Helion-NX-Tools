"""BlockStyler dialog helpers."""
import NXOpen


def prompt_string(dlx_path, block_id, default=None):
    """Show a single-field string BlockStyler dialog and return its value.

    Returns the stripped field value, or None if the user cancels. If `default`
    is given it is pre-filled into the field (editable by the user); otherwise
    the field is cleared, so a value from a previous run never carries over.

    BlockStyler dialogs require callback handlers to be registered (NX errors
    with "The Initialize callback is not registered" otherwise), and block
    values must be read inside the OK/Apply callback.
    """
    the_ui = NXOpen.UI.GetUI()
    dialog = the_ui.CreateDialog(dlx_path)
    captured = {}

    def _reset():
        """Set the field to `default`, or clear it when there is none."""
        text = default or ""
        props = dialog.GetBlockProperties(block_id)
        # Set both storages: a KeyIn field reads "Value", a Wide field
        # reads "WideValue". Best-effort — never block the dialog.
        for key in ("Value", "WideValue"):
            try:
                props.SetString(key, text)
            except Exception:
                pass

    def initialize_cb():
        _reset()

    def shown_cb():
        # NX restores saved field values after initialize; reset again once
        # the dialog is actually on screen so a previous run's text never shows.
        _reset()

    def update_cb(block):
        return 0

    def apply_cb():
        props = dialog.GetBlockProperties(block_id)
        value = ""
        # Read WideValue first: for a Wide-presentation field that is the live
        # edited text, while "Value" may still hold the initialize prefill.
        for key in ("WideValue", "Value"):
            try:
                candidate = props.GetString(key)
            except Exception:
                candidate = ""
            if candidate:
                value = candidate
                break
        captured["value"] = value
        return 0

    def ok_cb():
        apply_cb()

    dialog.AddInitializeHandler(initialize_cb)
    dialog.AddDialogShownHandler(shown_cb)
    dialog.AddUpdateHandler(update_cb)
    dialog.AddOkHandler(ok_cb)
    dialog.AddApplyHandler(apply_cb)

    try:
        response = dialog.Show()
        if response != NXOpen.Selection.Response.Ok:
            return None
        return (captured.get("value") or "").strip()
    finally:
        dialog.Dispose()


def choose_from_list(dlx_path, list_id, items, heading=None, heading_id=None, skip_id=None,
                     on_shown=None):
    """Show a BlockStyler dialog with a single-select list box; return (item, skip).

    `dlx_path` is the dialog file; `list_id` is the API name of its list box and
    `items` the strings to list. `heading` is put into the label block `heading_id`
    (if both are given), and `skip_id` names an optional toggle (for example "stop
    asking") whose state is returned as `skip`. `on_shown`, if given, is called with no
    arguments just before the dialog opens and again once it is on screen (a modal
    dialog can redraw the graphics window and drop a highlight, so callers use it to
    re-apply one). Errors raised by `on_shown` are ignored.

    Returns (chosen string, skip): the chosen string is None if the user cancelled,
    closed the dialog, or pressed OK with nothing selected. `skip` is the toggle's
    state at the end (False when there is no toggle), also reported on Cancel so a
    "skip all" can be combined with skipping this one.

    Like prompt_string, BlockStyler needs its callbacks registered and block values
    read inside the callbacks; the selection is read in the OK/Apply callback.
    """
    items = list(items)
    the_ui = NXOpen.UI.GetUI()
    dialog = the_ui.CreateDialog(dlx_path)
    captured = {"item": None, "skip": False}

    def _skip_value():
        if not skip_id:
            return False
        try:
            return bool(dialog.GetBlockProperties(skip_id).GetLogical("Value"))
        except Exception:
            return False

    def initialize_cb():
        if heading_id and heading:
            try:
                dialog.GetBlockProperties(heading_id).SetString("Label", heading)
            except Exception:
                pass
        try:
            dialog.TopBlock.FindBlock(list_id).SetListItems(items)
        except Exception:
            dialog.GetBlockProperties(list_id).SetStrings("ListItems", items)
        if skip_id:
            try:
                dialog.GetBlockProperties(skip_id).SetLogical("Value", False)
            except Exception:
                pass

    def _notify_shown():
        if on_shown is not None:
            try:
                on_shown()
            except Exception:
                pass

    def shown_cb():
        _notify_shown()

    def update_cb(block):
        captured["skip"] = _skip_value()
        return 0

    def apply_cb():
        chosen = None
        try:
            selected = dialog.TopBlock.FindBlock(list_id).GetSelectedItems()
            if selected:
                chosen = items[selected[0]]
        except Exception:
            try:
                chosen = dialog.TopBlock.FindBlock(list_id).SelectedItemString or None
            except Exception:
                chosen = None
        captured["item"] = chosen
        captured["skip"] = _skip_value()
        return 0

    def ok_cb():
        return apply_cb()

    def cancel_cb():
        captured["skip"] = _skip_value()
        return 0

    dialog.AddInitializeHandler(initialize_cb)
    dialog.AddDialogShownHandler(shown_cb)
    dialog.AddUpdateHandler(update_cb)
    dialog.AddOkHandler(ok_cb)
    dialog.AddApplyHandler(apply_cb)
    dialog.AddCancelHandler(cancel_cb)

    try:
        _notify_shown()
        response = dialog.Show()
        if response != NXOpen.Selection.Response.Ok:
            return None, captured["skip"]
        return captured["item"], captured["skip"]
    finally:
        dialog.Dispose()


def ask_yes_no(title, message):
    """Show a modal Yes/No question box; True if the user chose Yes.

    NXMessageBox.Show returns the 1-based index of the clicked button; for
    DialogType.Question the first button is Yes. Anything else (No, closing
    the box) counts as No.
    """
    response = NXOpen.UI.GetUI().NXMessageBox.Show(
        title, NXOpen.NXMessageBox.DialogType.Question, message)
    return response == 1
