# Assign Material (NX Open)

NX Open (Python) script for **NX 2506**. It assigns **one material** from the Helion material library
to the **bodies you select** in the **current part**, then **colors those bodies** to match the material
(color and translucency from `Materials/NX_Materials.csv`, the same values Color-By-Material uses) and finally
**updates the part's mass properties** so the weight reflects the new material.

Script: `NX-Scripts/Assign-Material/assign_material.py`

For assigning materials to a whole assembly and coloring it, use
[Color-By-Material](../Color-By-Material/README.md) (`assign_and_color_materials.py`).

## Run it

1. Open the part in **NX 2506**. The script uses the **work part**, so in an assembly make the part you
   want the work part first (right-click it, **Make Work Part**).
2. **File → Execute → NX Open…** and pick `assign_material.py`.
3. **Select the bodies** in the graphics window (they highlight), then click **OK**. Only **solid bodies of
   the current part** can be selected; anything else is skipped and listed. The selected bodies get the
   material **even if they already have one, which is replaced**.
4. A dialog lists the material library, with your bodies highlighted.
   * **Search box:** type part of a name and press **Enter** (or Tab). Every word must appear in the name, in
     any order, ignoring case: `alum 60` finds `Aluminum 6061`. If exactly one material matches it is
     selected for you. Clear the box and press Enter to see everything again.
   * Select a material and press **OK**. **Cancel**, or OK with nothing selected, changes nothing.
   * The heading tells you what is about to happen, for example
     `1150201-500/01: 2 bodies selected, 1 already have a material that will be REPLACED. Pick one:`.
5. The **Listing Window** reports the material, the color that was applied, which bodies were assigned (with `(replaced <old material>)`
   where one was replaced), and any failure with NX's reason.

## Good to know

* **Only the bodies you select are changed.** Everything else keeps its material.
* **If NX accepts an assignment but the body still has its old material, that is reported as a failure**,
  not a success, and nothing is kept for that run if no body changed.
* **Color:** the color is a body-level display override on the selected bodies. A material with no color or
  translucency in the CSV leaves the body color as it was (the listing says so). If the color cannot be set,
  the material is still assigned and the listing says why.
* **Mass properties:** updated last, like **Analysis → Mass Properties → Update Now** on the part. If that fails
  (for example no license) the material and color are kept and the listing says why.
* **One undo step.** Use **Edit → Undo** to take the assignment and color back (including replacements).
* **Nothing is saved.** Review the part, then save it yourself. A **read-only** part (for example not
  checked out of Teamcenter) can be assigned in the session but cannot be saved over the original; the
  script warns you.
* Cancelling the body selection (**Back** or **Cancel**), or clicking OK with nothing usable selected,
  changes nothing.
* The material is loaded from the Helion MatML library files on the NXcustom share (NX's own default
  library is switched off at the site), the same way as the Color-By-Material scripts.

## Files

* `assign_material.py`: the script (thin; the logic is in `lib/part_materials.py`).
* `ASSIGN_MATERIAL_PART_dialog.dlx`: the material dialog. It is the same list-with-search dialog as
  `Color-By-Material/ASSIGN_MATERIAL_dialog.dlx` (same heading, search box and list box), without the two
  per-body toggles ("Stop asking", "Cancel the whole operation"), which only make sense when a script
  asks about many bodies.
* Related: `lib/part_materials.py` (`pick_bodies`, `assign_material_to_part`), `lib/assemblies.py`
  (`assign_material`), `lib/nx_dialogs.py` (`choose_from_list`), `Materials/NX_Materials.csv`
  (the material names).
