# Color By Material (NX Open)

NX Open (Python) script for **NX 2506**. It walks the displayed assembly and
colors every body according to its **NX physical material**, using the hex codes
in `Materials/NX_Materials.csv`. A body whose material is `G-10 Garolite` gets
whatever color that row has in the `color` column.

Two scripts in `NX-Scripts/Color-By-Material/`:

| Script | Assembly color overrides |
| --- | --- |
| `color_by_material.py` | **Cleared** on every component first, so the new part colors show |
| `color_by_material_asm_leave_color.py` | **Left alone**; a component with an override keeps showing it |

They are otherwise identical. Use `color_by_material_asm_leave_color.py` when you
want to keep colors someone set deliberately in the assembly. Everything below
applies to both, except the override-clearing step noted in
[What it does](#what-it-does).

## Before you run it

* Open the **assembly** in NX 2506 (it must be fully loaded, or unloaded
  components are skipped).
* **Check out the parts you want to change** if you are in Teamcenter. The color
  is written into each component's own part, and read-only parts cannot be saved
  (see [Read-only parts](#read-only-parts)).
* Add hex codes to the `color` column of `Materials/NX_Materials.csv` for the
  materials you want colored (see [Material colors](#material-colors)).
* **Try it on a copy of the assembly first.** It modifies the component parts,
  and a part's color then changes in every assembly that uses it.

## Run it

1. In NX: **File → Execute → NX Open…** and pick `color_by_material.py` (or
   `color_by_material_asm_leave_color.py`).
2. Read the Listing Window.
3. Review the result in the graphics window, then **File → Save All** to keep it.
   The script never saves for you.

## What it does

1. Loads every row of `Materials/NX_Materials.csv` that has a `color`.
2. **`color_by_material.py` only:** clears the assembly-level color override on
   every component (the same as unticking *Specific color* in Edit → Properties),
   so part colors are visible. `color_by_material_asm_leave_color.py` skips this
   step, which is the only difference (each script is a few lines that call
   `lib/color_by_material.py` with `clear_overrides` `True` or `False`).
3. Collects each **distinct part** in the assembly once, however many instances
   there are.
4. For each part, makes it the work part, reads the NX material of each body, and
   sets the body (and all its faces) to the color for that material. Then it
   switches back to your displayed part.

Suppressed and unloaded components are ignored.

## Material colors

`Materials/NX_Materials.csv` lists every material from the Helion NX libraries.
The `color` column is hand-maintained, in hex:

```
name,...,color
G-10 Garolite,...,#03fcad
Stainless Steel 304,...,#bcc3c4
```

* Materials are matched by **name**, case-insensitively, against the material
  assigned to the body in NX.
* A material with no `color` leaves its bodies unchanged.
* Rebuilding the CSV with `Materials/build_nx_materials_csv.py` keeps the `color`
  column; it carries colors over by material name.

### The NX palette limit

NX bodies can only use the **216-color NX palette**, so each hex code is mapped to
the **nearest palette color**. `#03fcad` will be close, not exact. The Listing
Window shows the NX color number that was used for each body so you can see what
you got.

## The Listing Window

```
12 materials have a color in ...\Materials\NX_Materials.csv
36 distinct parts in the assembly
Cleared assembly color override on 36 components   (color_by_material.py only)

Bodies colored (part / body -> material, NX color):
  91247A505/NC / 91247A505_... Hex Head Screw -> Alloy Steel, NX color 91  (used x4)

Colored 34 bodies in 21 parts (modified, NOT saved).
```

At the end it also lists:

* **Read-only parts**, which were colored in this session only.
* **Skipped parts**, which NX would not let the script change, with the reason.
* **Left unchanged**, the materials that had no color in the CSV, plus bodies with
  no material (`(none)`), each with a count.

## Read-only parts

Read-only parts (for example, not checked out of Teamcenter) are still colored in
your session and are listed in the Listing Window. They cannot be saved over their
own file, so those colors will not persist. Check the part out and run the script
again if you want to keep them.

## If a body doesn't change color

* **No material** — it shows as `(none)` in the unchanged list. Assign a material in
  NX first.
* **No color for its material** — add a hex code for that material in the CSV. Check
  the spelling matches the material name in NX.
* **An assembly color override** — with `color_by_material_asm_leave_color.py`
  this is expected: the override on the component hides the new part color. Run
  `color_by_material.py` to clear it.
* **A body-level color override** — neither script clears these. A color set
  directly on a body occurrence in the assembly can still hide the part color.

## Related files

* `lib/color_by_material.py` — the shared implementation (`run(clear_overrides)`)
  both scripts call. Change behavior here, not in the scripts.
* `lib/colors.py` — hex → nearest NX color, `set_body_color`,
  `clear_component_color_override`.
* `lib/assemblies.py` — `walk_components`, `get_bodies`, `get_body_material`.
* `Materials/build_nx_materials_csv.py` — regenerates the CSV from the XML
  material libraries in a dated folder under `Materials/`.
* `example_journals/remove_assebly_color_override.py` — the recorded journal the
  override-clearing code is based on.
