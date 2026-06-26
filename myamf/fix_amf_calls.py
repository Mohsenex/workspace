#!/usr/bin/env python3
"""
Sweep myamf/*.py and route AMF fixed-cell calls through ported_cells / get_component.

Rules (from AMF PDK 5.0 port scan):
  ssc_via()  -> ssc_via()      (portless -> wrapper)
  mmi_2x2()     -> mmi_2x2()       (portless -> wrapper)
  mmi_1x2()     -> mmi_1x2()       (native ports via PDK)
Also rewrites the pdk.get_component("...") form of those three to the same helpers,
fixes the `<var>.xmin = die.xmin - 6` floorplan overshoot, and inserts the import.

Idempotent: safe to run repeatedly. Prints a per-file summary. Use --apply to write;
default is a dry run.
"""
import os, re, sys, argparse

ROOT = "/workspace/myamf"
IMPORT_LINE = "from .ported_cells import ssc_via, mmi_1x2, mmi_2x2"
SKIP = {"ported_cells.py", "__init__.py"}

# (regex, replacement) — bare factory calls and the get_component string form
SUBS = [
    (r'AMF_300LSOI_LSiN2SOISSC_Cband_v5p0\s*\(\s*\)', 'ssc_via()'),
    (r'AMF_300LSOI_Si2X2MMI_Cband_v5p0\s*\(\s*\)',    'mmi_2x2()'),
    (r'AMF_300LSOI_Si1X2MMI_Cband_v5p0\s*\(\s*\)',    'mmi_1x2()'),
    (r'(?:pdk|get_active_pdk\(\))\.get_component\(\s*["\']AMF_300LSOI_LSiN2SOISSC_Cband_v5p0["\']\s*\)', 'ssc_via()'),
    (r'(?:pdk|get_active_pdk\(\))\.get_component\(\s*["\']AMF_300LSOI_Si2X2MMI_Cband_v5p0["\']\s*\)',    'mmi_2x2()'),
    (r'(?:pdk|get_active_pdk\(\))\.get_component\(\s*["\']AMF_300LSOI_Si1X2MMI_Cband_v5p0["\']\s*\)',    'mmi_1x2()'),
]
FLOORPLAN = (r'(\w+)\.xmin\s*=\s*die\.xmin\s*-\s*6\b', r'\1.xmin = die.xmin')

def fix_text(text):
    changes = []
    for pat, rep in SUBS:
        text, n = re.subn(pat, rep, text)
        if n: changes.append(f"{n}x {rep}")
    text, n = re.subn(*FLOORPLAN, text)
    if n: changes.append(f"{n}x floorplan -6 fix")
    # add import only if a helper is now used and import not present
    if any(h in text for h in ("ssc_via(", "mmi_1x2(", "mmi_2x2(")) and IMPORT_LINE not in text:
        if "import gdsfactory as gf" in text:
            text = text.replace("import gdsfactory as gf",
                                "import gdsfactory as gf\n" + IMPORT_LINE, 1)
        else:
            text = IMPORT_LINE + "\n" + text
        changes.append("added import")
    return text, changes

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=ROOT)
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry run)")
    args = ap.parse_args()
    total = 0
    for fn in sorted(os.listdir(args.root)):
        if not fn.endswith(".py") or fn in SKIP: continue
        path = os.path.join(args.root, fn)
        src = open(path).read()
        new, changes = fix_text(src)
        if changes:
            total += 1
            print(f"{fn}: {', '.join(changes)}")
            if args.apply:
                open(path, "w").write(new)
    if total == 0:
        print("No changes needed (all files already routed).")
    else:
        print(f"\n{'APPLIED to' if args.apply else 'WOULD change'} {total} file(s).")
        if not args.apply:
            print("Re-run with --apply to write.")

if __name__ == "__main__":
    main()
