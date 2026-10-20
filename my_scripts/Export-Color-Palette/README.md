# Export Color Palette (NX Open)

NX Open (Python) script for **NX 2506**. It saves NX's color palette (color IDs 1-216 and
their RGB and hex values) to `Materials/nx_color_palette.csv`.

Script: `my_scripts/Export-Color-Palette/export_color_palette.py` (personal, git-ignored)

## Why

A material's `color` in `Materials/NX_Materials.csv` can be a hex code (`#03fcad`) or an
**NX color ID** (`63`). A hex code is easy to draw, but an ID is just a number: what color
it is depends on NX's palette. This script asks NX itself, so the swatch PDF
(`my_scripts/make_color_swatch_pdf.py`, a personal script) can show the real color for every ID, as `NX ID 63 = #rrggbb`.
It uses the same call the Color-By-Material scripts use to map hex codes to IDs, so it is the exact
mapping they apply.

## Run it

1. Open **NX 2506** and open **any part** (NX needs a part to read its palette).
2. **File → Execute → NX Open…** and pick `export_color_palette.py`.
3. The Listing Window prints how many colors were written and a few examples.

Then rebuild the PDF: `py my_scripts\make_color_swatch_pdf.py` (it writes `Materials/NX_Materials_colors.pdf`).

## Output

`Materials/nx_color_palette.csv`, one row per color:

```
id,r,g,b,hex
1,...,#......
...
216,...,#......
```

The file is small, so commit it. Re-run the script only if the site's NX color palette changes.

## Good to know

* Until this file exists, the PDF draws NX-ID colors as a hatched box labeled with the ID.
* Read-only for NX: it changes no part and only writes the CSV.
* The values are NX's palette for the part you have open. A site that customizes the palette
  per user or per part could see different values; export from a typical part.
