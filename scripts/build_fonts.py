#!/usr/bin/env python3
"""Builds the WOFF2 files in assets/fonts/ from the official variable fonts (SIL OFL 1.1).

Sources (google/fonts on GitHub, ofl/inter and ofl/playfairdisplay):
  Inter[opsz,wght].ttf  PlayfairDisplay[wght].ttf  PlayfairDisplay-Italic[wght].ttf
Each weight in use is cut out of the variable font (Inter at its text optical size, 14), then subset to
Latin: Basic Latin and Latin-1 (all Spanish letters), Latin Extended-A (Hungarian and Romanian names),
U+0218 to U+021B (the comma-below letters in "Babeș-Bolyai"), general punctuation, the euro sign and the
two arrows the site uses. Weights: see the css in assets/css/tokens.css.

Usage: python3 scripts/build_fonts.py SOURCE_DIR   (needs: pip install fonttools brotli)
"""
import sys
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools import subset

UNICODES = ("U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,"
            "U+2000-206F,U+20AC,U+2122,U+2190,U+2191,U+2192,U+2193,U+2212,U+2215,U+FEFF,U+FFFD,"
            "U+0100-017F,U+0218-021B")

JOBS = [  # (source file, axes to pin, output)
    ("Inter[opsz,wght].ttf", {"opsz": 14, "wght": 400}, "inter-latin-400.woff2"),
    ("Inter[opsz,wght].ttf", {"opsz": 14, "wght": 500}, "inter-latin-500.woff2"),
    ("Inter[opsz,wght].ttf", {"opsz": 14, "wght": 600}, "inter-latin-600.woff2"),
    ("PlayfairDisplay[wght].ttf", {"wght": 600}, "playfair-display-latin-600.woff2"),
    ("PlayfairDisplay[wght].ttf", {"wght": 700}, "playfair-display-latin-700.woff2"),
    ("PlayfairDisplay-Italic[wght].ttf", {"wght": 600}, "playfair-display-latin-600-italic.woff2"),
]


def unicodes():
    out = []
    for part in UNICODES.split(","):
        lo, _, hi = part[2:].partition("-")
        out.extend(range(int(lo, 16), int(hi or lo, 16) + 1))
    return out


def main(src, dest):
    for name, axes, out in JOBS:
        font = TTFont(Path(src) / name)
        font = instancer.instantiateVariableFont(font, axes)
        opts = subset.Options()
        opts.flavor = "woff2"
        opts.layout_features = subset.Options().layout_features + ["tnum"]  # tnum: tabular-nums in dates and years
        opts.name_IDs = [0, 1, 2, 3, 4, 6, 13, 14]  # keep the copyright and license notices
        opts.notdef_outline = True
        sub = subset.Subsetter(opts)
        sub.populate(unicodes=unicodes())
        sub.subset(font)
        target = Path(dest) / out
        subset.save_font(font, target, opts)
        print(f"{out}: {target.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main(sys.argv[1], Path(__file__).resolve().parent.parent / "assets" / "fonts")
