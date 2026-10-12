"""BlockStyler dialog helpers."""
import NXOpen


def prompt_string(dlx_path, block_id, default=None):
    """Show a single-field string BlockStyler dialog and return its value.

    Returns the stripped field value, or None if the user cancels. If `default`
    is given it is pre-filled into the field (editable by the user).

    BlockStyler dialogs require callback handlers to be registered (NX errors
    with "The Initialize callback is not registered" otherwise), and block
    values must be read inside the OK/Apply callback.
    """
    the_ui = NXOpen.UI.GetUI()
    dialog = the_ui.CreateDialog(dlx_path)
    captured = {}

    def initialize_cb():
        if default:
            props = dialog.GetBlockProperties(block_id)
            # Set both storages: a KeyIn field reads "Value", a Wide field
            # reads "WideValue". Best-effort — never block the dialog.
            for key in ("Value", "WideValue"):
                try:
                    props.SetString(key, default)
                except Exception:
                    pass

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


def ask_yes_no(title, message):
    """Show a modal Yes/No question box; True if the user chose Yes.

    NXMessageBox.Show returns the 1-based index of the clicked button; for
    DialogType.Question the first button is Yes. Anything else (No, closing
    the box) counts as No.
    """
    response = NXOpen.UI.GetUI().NXMessageBox.Show(
        title, NXOpen.NXMessageBox.DialogType.Question, message)
    return response == 1
