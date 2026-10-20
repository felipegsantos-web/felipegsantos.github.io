#!/usr/bin/env python3
"""Contrast check for every text/background pair the site's CSS defines, in both themes.

Colours come from assets/css/tokens.css (design tokens) and, for the colours that are written
as literals in assets/css/components.css (publication and news badges, research theme colours),
from that file. Text needs 4.5:1 (WCAG 1.4.3); icons, focus rings and component outlines need
3:1 (WCAG 1.4.11). Translucent backgrounds (color-mix with transparent) are composited over the
background they sit on, as the browser does.

Usage:
  python3 scripts/check_contrast.py                 # check assets/css, exit 1 on any failure
  python3 scripts/check_contrast.py --markdown      # table for a pull request
  python3 scripts/check_contrast.py --css-dir DIR   # check another copy of the css files
"""
import argparse
import math
import re
import sys
from pathlib import Path

# --- colour maths --------------------------------------------------------------------------


def hex_to_rgb(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def rgb_to_hex(c):
    return "#" + "".join(f"{round(max(0, min(1, v)) * 255):02X}" for v in c)


def lin(v):
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def delin(v):
    return 12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055


def luminance(c):
    r, g, b = (lin(v) for v in c)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(a, b):
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def to_oklab(c):
    r, g, b = (lin(v) for v in c)
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l, m, s = (math.copysign(abs(x) ** (1 / 3), x) for x in (l, m, s))
    return (0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
            1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
            0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s)


def from_oklab(lab):
    L, a, b = lab
    l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    r = 4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    bl = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
    return tuple(max(0, min(1, delin(max(0, v)))) for v in (r, g, bl))


def mix(a, pct, b):
    """color-mix(in oklab, a pct%, b) for two opaque colours."""
    la, lb = to_oklab(a), to_oklab(b)
    t = pct / 100
    return from_oklab(tuple(x * t + y * (1 - t) for x, y in zip(la, lb)))


def over(fg, alpha, base):
    """fg at the given alpha composited over base (sRGB, like the browser)."""
    return tuple(f * alpha + b * (1 - alpha) for f, b in zip(fg, base))


# --- reading the css ----------------------------------------------------------------------


def block(css, selector):
    m = re.search(re.escape(selector) + r"\s*\{(.*?)\n\}", css, re.S)
    return m.group(1) if m else ""


def props(body):
    return dict(re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", body))


def resolve(name, table, depth=0):
    """Resolve a token to an RGB tuple (var() chains and color-mix with another colour)."""
    val = table[name].strip()
    m = re.fullmatch(r"var\((--[\w-]+)\)", val)
    if m:
        return resolve(m.group(1), table, depth + 1)
    m = re.fullmatch(r"color-mix\(in oklab,\s*var\((--[\w-]+)\)\s*(\d+)%,\s*var\((--[\w-]+)\)\)", val)
    if m:
        return mix(resolve(m.group(1), table), int(m.group(2)), resolve(m.group(3), table))
    if re.fullmatch(r"#[0-9A-Fa-f]{3,6}", val):
        return hex_to_rgb(val)
    raise ValueError(f"cannot resolve {name}: {val}")


def load(css_dir):
    tokens = Path(css_dir, "tokens.css").read_text()
    comps = Path(css_dir, "components.css").read_text()
    light = props(block(tokens, ":root"))
    dark = {**light, **props(block(tokens, "[data-theme='dark']"))}
    themes = {"light": light, "dark": dark}
    # colours written as literals in components.css
    badges = {m[0]: (m[1], m[2]) for m in re.findall(
        r"\.type-badge--(\w+)\{background:(#\w+);color:(#\w+)\}", comps)}
    news = {m[0]: (m[1], m[2]) for m in re.findall(
        r"\.news-item__type--(pub|media)\{background:(#\w+);color:(#\w+)\}", comps)}
    theme_colors = {"light": {}, "dark": {}}
    for sel, col in re.findall(r"(?<![\w-])((?:\[data-theme='dark'\] )?\.theme--\w+)\{--theme-color:(#\w+)\}", comps):
        name = sel.split("--")[-1]
        theme_colors["dark" if sel.startswith("[") else "light"][name] = col
    for name, col in theme_colors["light"].items():
        theme_colors["dark"].setdefault(name, col)
    return themes, badges, news, theme_colors


# --- the pairs ----------------------------------------------------------------------------

TEXT, UI = 4.5, 3.0


def pairs_for(theme, t, badges, news, theme_colors):
    """Yield (group, description, fg, bg, minimum ratio, fg label, bg label)."""
    R = lambda n: resolve(n, t)
    surfaces = ["--bg", "--bg-alt", "--bg-card"]
    out = []

    def add(group, desc, fg, bg, need, fl, bl):
        out.append((group, desc, fg, bg, need, fl, bl))

    for fg in ("--text", "--text-secondary", "--text-muted", "--accent", "--accent-hover"):
        for bg in surfaces:
            use = {"--text": "body text", "--text-secondary": "secondary text",
                   "--text-muted": "muted text (intros, authors, venue, dates, nav, footer, filters, language switch)",
                   "--accent": "links, eyebrows, active nav", "--accent-hover": "link hover"}[fg]
            add("Text", use, R(fg), R(bg), TEXT, fg, bg)
    # tinted surfaces
    why_bg = over(R("--accent"), 0.05, R("--bg-card"))
    funder_bg = over(R("--accent"), 0.10, R("--bg-card"))
    add("Text", "muted text in the 'why it matters' box", R("--text-muted"), why_bg, TEXT, "--text-muted", "accent 5% on --bg-card")
    add("Text", "'why it matters' label", R("--accent"), why_bg, TEXT, "--accent", "accent 5% on --bg-card")
    add("Tags", "project funding tag", R("--accent"), funder_bg, TEXT, "--accent", "accent 10% on --bg-card")
    add("Tags", "ongoing pill", R("--accent"), R("--teal-bg"), TEXT, "--accent", "--teal-bg")
    # buttons and active controls
    add("Buttons", "primary button, active filter and language, skip link", R("--text-inv"), R("--accent"), TEXT, "--text-inv", "--accent")
    add("Buttons", "primary button hover", R("--text-inv"), R("--accent-hover"), TEXT, "--text-inv", "--accent-hover")
    add("Buttons", "secondary button hover and tag hover", R("--accent"), R("--accent-soft"), TEXT, "--accent", "--accent-soft")
    add("Buttons", "PDF link (outlined)", R("--accent"), R("--bg-card"), TEXT, "--accent", "--bg-card")
    add("Buttons", "PDF link hover", R("--bg"), R("--accent"), TEXT, "--bg", "--accent")
    # publication, media and news badges
    for k, (bg, fg) in badges.items():
        add("Badges", f"publication badge: {k}", hex_to_rgb(fg), hex_to_rgb(bg), TEXT, fg, bg)
    for k, (bg, fg) in news.items():
        add("Badges", f"news badge: {k}", hex_to_rgb(fg), hex_to_rgb(bg), TEXT, fg, bg)
    for name, tok in (("press", "--accent"), ("radio", "--pub-book"), ("podcast", "--accent"), ("opinion", "--pub-review")):
        bg = over(R(tok), 0.12, R("--bg-card"))
        add("Badges", f"media badge: {name}", R(tok), bg, TEXT, tok, f"{tok} 12% on --bg-card")
    for name, tok in (("review", "--pub-review"), ("forthcoming", "--pub-review")):
        add("Badges", f"status pill: {name}", R(tok), R(tok + "-bg"), TEXT, tok, tok + "-bg")
    add("Badges", "status pill: draft", R("--text-secondary"), R("--bg-alt"), TEXT, "--text-secondary", "--bg-alt")
    add("Badges", "status pill: revise and resubmit", R("--info"), over(R("--info"), 0.10, R("--bg")), TEXT, "--info", "info 10% on --bg")
    # research theme colours (count text on the theme cards, left border)
    for name, col in sorted(theme_colors[theme].items()):
        add("Theme cards", f"theme card count: {name}", hex_to_rgb(col), R("--bg-card"), TEXT, col, "--bg-card")
        add("Theme cards", f"theme card border: {name}", hex_to_rgb(col), R("--bg-card"), UI, col, "--bg-card")
    # non-text
    for bg in surfaces:
        add("Non-text", "focus ring (3px outline)", R("--accent"), R(bg), UI, "--accent", bg)
    for fg, desc in (("--text-muted", "icon buttons (theme toggle, profile icons)"), ("--accent", "accent borders and active states")):
        for bg in surfaces:
            add("Non-text", desc, R(fg), R(bg), UI, fg, bg)
    add("Non-text", "active control fill against the page", R("--accent"), R("--bg"), UI, "--accent", "--bg")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--css-dir", default=str(Path(__file__).resolve().parent.parent / "assets" / "css"))
    ap.add_argument("--markdown", action="store_true")
    args = ap.parse_args()
    themes, badges, news, theme_colors = load(args.css_dir)
    failures = 0
    rows = []
    for theme, t in themes.items():
        for group, desc, fg, bg, need, fl, bl in pairs_for(theme, t, badges, news, theme_colors):
            r = ratio(fg, bg)
            ok = r + 1e-9 >= need
            failures += not ok
            rows.append((theme, group, desc, fl, rgb_to_hex(fg), bl, rgb_to_hex(bg), need, r, ok))
    if args.markdown:
        print("| Theme | Pair | Foreground | Background | Ratio | Needs | Result |")
        print("|---|---|---|---|---|---|---|")
        for theme, group, desc, fl, fh, bl, bh, need, r, ok in rows:
            print(f"| {theme} | {desc} | `{fh}` ({fl}) | `{bh}` ({bl}) | {r:.2f} | {need:g} | {'pass' if ok else 'FAIL'} |")
    else:
        for theme, group, desc, fl, fh, bl, bh, need, r, ok in rows:
            if not ok:
                print(f"FAIL {theme:5} {r:5.2f} < {need:g}  {desc}: {fh} ({fl}) on {bh} ({bl})")
    print(f"{len(rows)} pairs checked, {failures} below the minimum", file=sys.stderr if args.markdown else sys.stdout)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
