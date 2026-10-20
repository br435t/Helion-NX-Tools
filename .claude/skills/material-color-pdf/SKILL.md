---
name: material-color-pdf
description: Use when the user wants to see, visualize, preview, print or share the material colors in Materials/NX_Materials.csv, or asks for the color swatch PDF, a "color to pdf", or to refresh/regenerate it after editing the CSV's color or Transparency columns. Builds Materials/NX_Materials_colors.pdf, one swatch per material with its name above it.
---

# Material color swatch PDF

Builds `Materials/NX_Materials_colors.pdf` from the `color` and `Transparency` columns of
`Materials/NX_Materials.csv`: each material's name with a color swatch underneath, and the
color value and transparency below the swatch. The generator is
`my_scripts/make_color_swatch_pdf.py`. Do not rewrite it; run it. That script is **personal and
git-ignored** (it only exists on the machine of whoever made it). It reads and writes the shared
files in `Materials/`, so it runs from any folder. If it is missing, tell the user instead of
recreating it: it is theirs to share or restore.

## Steps

1. **Run the generator** with the repo's venv Python (it has `reportlab`), from the repo root:

   ```
   .venv\Scripts\python.exe my_scripts\make_color_swatch_pdf.py
   ```

   It prints `Wrote N swatches (M materials without a color skipped) to <path>`. If the
   venv is missing, run `setup.bat` first, or `pip install reportlab` into whichever Python
   you use. If the CSV is open in Excel it can still be read, but if the PDF is open in a
   viewer, writing it fails with `PermissionError`; ask the user to close it.

2. **Check the result.** Confirm the count in the printed line matches the number of CSV rows
   that have a color, and that the file exists. To look at it, render a page to PNG (for
   example with `pypdfium2`, installed with `pip install --target <scratch dir> pypdfium2`
   so the repo's environment is untouched) and view that image. Do not claim it looks right
   without having looked, when a visual check is possible.

3. **Report to the user:** the PDF path, how many materials are shown, and how many were
   skipped for having no color. Mention anything in the notes below that applies.

## What to tell the user

- **Materials with no `color`** are left out of the PDF (counted in its footer).
- **A color given as an NX color ID** (a whole number 1-216 instead of a hex code) is drawn from
  `Materials/nx_color_palette.csv`, labeled `NX ID <n> = #rrggbb`. That file is written from inside
  NX by `my_scripts/Export-Color-Palette/export_color_palette.py` (run it with any part open). If
  the file is missing, the ID shows as a hatched box; tell the user to run that NX script once,
  then regenerate.
- **Transparency is a text label only**; swatches are drawn solid, so a material at
  transparency 90 still shows its full color.
- **The swatch is the hex code, not the NX display color.** NX maps each hex code to the
  nearest of its 216 palette colors when the coloring scripts run, so the model can look
  slightly different from the PDF. Use an NX color ID in the CSV for an exact palette color.

## Changing the PDF

Layout is set by constants at the top of `my_scripts/make_color_swatch_pdf.py`: `COLS`, `ROWS`
(swatches per page), the fonts and sizes, and `NAME_LINES` (how many lines a long name may wrap
to before it is cut with `...`). Edit those, then re-run and re-check the result as above.
Entries are sorted by name; the `Source` line and footer text are in the `draw` function.

## Related

- `Materials/NX_Materials.csv`: the data. The `color` and `Transparency` columns are
  hand-maintained, and `Materials/build_nx_materials_csv.py` keeps them when it rebuilds the CSV.
- `NX-Scripts/Color-By-Material/`: the scripts that apply these colors in NX. See its README for
  how hex codes and color IDs are interpreted.
