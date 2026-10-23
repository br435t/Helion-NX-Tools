# Assign Material (NX Open)

NX Open (Python) script for **NX 2506**. It assigns **one material** from the Helion material library
to every body of the **current part** that has none. It only assigns: no colors are touched.

Script: `NX-Scripts/Assign-Material/assign_material.py`

For assigning materials *and* coloring a whole assembly, use
[Color-By-Material](../Color-By-Material/README.md) (`assign_and_color_materials.py`).

## Run it

1. Open the part in **NX 2506**. The script uses the **work part**, so in an assembly make the part you
   want the work part first (right-click it, **Make Work Part**).
2. **File → Execute → NX Open…** and pick `assign_material.py`.
3. A dialog lists the material library. The bodies that are about to receive the material are
   **highlighted** in the graphics window while it is open.
   * **Search box:** type part of a name and press **Enter** (or Tab). Every word must appear in the name, in
     any order, ignoring case: `alum 60` finds `Aluminum 6061`. If exactly one material matches it is
     selected for you. Clear the box and press Enter to see everything again.
   * Select a material and press **OK**. **Cancel**, or OK with nothing selected, changes nothing.
4. The **Listing Window** reports the material, which bodies were assigned, and any failure with NX's reason.

## What it does and does not do

* **Only bodies with no material are changed.** Bodies that already have a material are left alone, so
  nothing existing is overwritten. The dialog heading says how many bodies are about to change
  (for example `1150201-500/01: 3 of 5 bodies have no material. Pick one for them:`), and the Listing
  Window says how many were left alone. If every body already has a material it says so and shows no dialog.
* **One undo step.** Use **Edit → Undo** to take the assignment back.
* **Nothing is saved.** Review the part, then save it yourself. A **read-only** part (for example not
  checked out of Teamcenter) can be assigned in the session but cannot be saved over the original; the
  script warns you.
* The material is loaded from the Helion MatML library files on the NXcustom share (NX's own default
  library is switched off at the site), the same way as the Color-By-Material scripts.

## Files

* `assign_material.py`: the script (thin; the logic is in `lib/part_materials.py`).
* `ASSIGN_MATERIAL_PART_dialog.dlx`: the dialog. It is the same list-with-search dialog as
  `Color-By-Material/ASSIGN_MATERIAL_dialog.dlx` (same heading, search box and list box), without the two
  per-body toggles ("Stop asking", "Cancel the whole operation"), which only make sense when a script
  asks about many bodies.
* Related: `lib/part_materials.py`, `lib/assemblies.py` (`assign_material`), `lib/nx_dialogs.py`
  (`choose_from_list`), `Materials/NX_Materials.csv` (the material names).
