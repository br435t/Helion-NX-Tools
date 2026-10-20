"""Build NX_Materials.csv from every *.xml material library in a dated folder.

Usage:  py build_nx_materials_csv.py [library_folder]
Default folder is the newest dated subfolder next to this script. The CSV is
written to this folder as NX_Materials.csv, one row per <Material>.
"""
import csv
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
FIELDS = ["source_file", "name", "class", "subclass", "material_type", "version",
          "alt_name", "description", "density_kg_m3", "youngs_modulus_raw",
          "poissons_ratio", "color", "Transparency"]


def _val(bd, *prefixes):
    for pd in bd.findall("PropertyData"):
        if any(pd.get("property", "").startswith(p) for p in prefixes):
            d = pd.find("Data")
            if d is not None and (d.text or "").strip():
                return " ".join(d.text.split())
    return ""


def _density(raw):
    """kg/m^3 as text. Blank for temperature-dependent tables (comma lists),
    which hold temperature/value pairs rather than a single density."""
    if not raw:
        return ""
    if "," in raw:
        return "temperature-dependent"
    v = float(raw)
    # Isotropic entries often store kg/mm^3 (Copper 8.92e-06); convert those.
    # Entries stored in g/cm^3 (e.g. 2.15) are NOT detectable and stay as-is.
    return "{0:.6g}".format(v * 1e9 if v < 1 else v)


def rows_from(path):
    for m in ET.parse(path).getroot().findall("Material"):
        bd = m.find("BulkDetails")
        yield {
            "source_file": os.path.basename(path),
            "name": bd.findtext("Name", "").strip(),
            "class": bd.findtext("Class/Name", "").strip(),
            "subclass": bd.findtext("Subclass/Name", "").strip(),
            "material_type": _val(bd, "Material Type"),
            "version": _val(bd, "Version_1"),
            "alt_name": _val(bd, "AltName_2"),
            "description": _val(bd, "Description_3"),
            "density_kg_m3": _density(_val(bd, "MassDensityConstant", "MassDensity_")),
            "youngs_modulus_raw": _val(bd, "YoungsModulusConstant"),
            "poissons_ratio": _val(bd, "PoissonsRatioConstant"),
        }


def main():
    if len(sys.argv) > 1:
        folder = sys.argv[1]
    else:
        # Newest subfolder that actually holds .xml libraries (ignores __pycache__ etc.).
        dated = sorted(
            d for d in os.listdir(HERE)
            if os.path.isdir(os.path.join(HERE, d))
            and any(f.lower().endswith(".xml") for f in os.listdir(os.path.join(HERE, d))))
        if not dated:
            sys.exit("No subfolder with .xml material libraries found in " + HERE)
        folder = os.path.join(HERE, dated[-1])
    rows = []
    for fn in sorted(os.listdir(folder)):
        if fn.lower().endswith(".xml"):
            rows.extend(rows_from(os.path.join(folder, fn)))
    if not rows:
        sys.exit("No <Material> entries found in {0}; leaving NX_Materials.csv alone.".format(folder))
    out = os.path.join(HERE, "NX_Materials.csv")
    # "color" (hex, e.g. #03fcad) and "Transparency" (0 opaque .. 100 clear) are
    # hand-maintained: carry them over from the existing CSV by material name so
    # a rebuild does not wipe them.
    kept = {}
    if os.path.isfile(out):
        with open(out, newline="", encoding="utf-8-sig") as f:
            kept = {r["name"]: r for r in csv.DictReader(f)}
    for r in rows:
        old = kept.get(r["name"], {})
        r["color"] = old.get("color", "")
        r["Transparency"] = old.get("Transparency", "")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    print("Wrote {0} materials from {1} to {2}".format(len(rows), folder, out))


main()
