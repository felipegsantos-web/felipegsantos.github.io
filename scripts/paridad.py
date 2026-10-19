#!/usr/bin/env python3
"""Compare two builds of the site page by page.

Usage: python3 scripts/paridad.py BASELINE_DIR SITE_DIR

BASELINE_DIR holds the compiled pages (a checkout of the old `main`), SITE_DIR is
the Jekyll output (`_site`). For every `index.html` in the baseline (root, en/, es/)
it compares:

  * visible text, whitespace normalised
  * <title> and every <meta>/<link> in document order (description, canonical,
    hreflang, Open Graph, Twitter, citation_*, icons, stylesheets, ...)
  * JSON-LD blocks, parsed (structures are compared, not strings)
  * the ordered list of links (href) and images (src, alt)
  * external script URLs and the text of inline scripts
  * scripting hooks: id, data-*, aria-*, role of every element, in order

Only two differences are tolerated, both listed in EXCEPTIONS below: the `?v=`
cache parameter and the two CV links that used to be broken. Exit status is 1 if
any other difference is found.
"""
import json
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup, Comment

# (page, old href) -> new href. Task 6 of the migration brief.
EXCEPTIONS = {
    ("en/cv/index.html", "../../publications/"): "/en/publications/",
    ("es/cv/index.html", "../../publicaciones/"): "/es/publicaciones/",
}

VERSION_RE = re.compile(r"\?v=[^\"'&#]*")


def pages(base: Path):
    found = [p.relative_to(base).as_posix() for p in base.rglob("index.html")]
    return sorted(
        p for p in found
        if p == "index.html" or p.startswith(("en/", "es/"))
    )


def norm_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def strip_version(value: str) -> str:
    return VERSION_RE.sub("", value)


def parse(path: Path) -> BeautifulSoup:
    return BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")


def visible_text(soup: BeautifulSoup) -> str:
    body = soup.find("body")
    if body is None:
        return ""
    clone = BeautifulSoup(str(body), "html.parser")
    for t in clone.find_all(["script", "style", "noscript", "template"]):
        t.decompose()
    for c in clone.find_all(string=lambda s: isinstance(s, Comment)):
        c.extract()
    return norm_ws(clone.get_text(""))


def head_items(soup: BeautifulSoup):
    items = []
    for el in soup.find_all(["meta", "link"]):
        attrs = {k: (" ".join(v) if isinstance(v, list) else v) for k, v in el.attrs.items()}
        attrs = {k: strip_version(v) for k, v in attrs.items()}
        in_head = el.find_parent("head") is not None
        items.append((el.name, in_head, tuple(sorted(attrs.items()))))
    return items


def jsonld(soup: BeautifulSoup):
    out = []
    for s in soup.find_all("script", attrs={"type": "application/ld+json"}):
        out.append(json.loads(s.string))
    return out


def links(soup: BeautifulSoup, page: str):
    out = []
    for a in soup.find_all("a"):
        if a.has_attr("href"):
            out.append(("a", a["href"]))
    return out


def images(soup: BeautifulSoup):
    return [(i.get("src"), i.get("alt")) for i in soup.find_all("img")]


def scripts(soup: BeautifulSoup):
    return [strip_version(s["src"]) for s in soup.find_all("script", src=True)]


def inline_scripts(soup: BeautifulSoup):
    return [
        norm_ws(t.get_text())
        for t in soup.find_all("script")
        if not t.has_attr("src") and t.get("type") != "application/ld+json"
    ]


def hooks(soup: BeautifulSoup):
    out = []
    for el in soup.find_all(True):
        keep = {
            k: (" ".join(v) if isinstance(v, list) else v)
            for k, v in el.attrs.items()
            if k in ("id", "role", "type", "name", "for", "target", "rel")
            or k.startswith(("data-", "aria-"))
        }
        out.append((el.name, tuple(sorted(keep.items()))))
    return out


def apply_exceptions(page: str, base_links):
    fixed = []
    for kind, href in base_links:
        fixed.append((kind, EXCEPTIONS.get((page, href), href)))
    return fixed


def first_diff(a, b):
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return i, x, y
    if len(a) != len(b):
        i = min(len(a), len(b))
        return i, a[i] if i < len(a) else None, b[i] if i < len(b) else None
    return None


def compare_page(base: Path, site: Path, page: str):
    problems = []
    bpath, spath = base / page, site / page
    if not spath.exists():
        return [f"missing in site: {page}"]
    b, s = parse(bpath), parse(spath)

    def check(label, x, y):
        if x != y:
            d = first_diff(x, y) if isinstance(x, list) else None
            problems.append(f"{label}: differs" + (f" at #{d[0]}\n      base: {d[1]!r}\n      site: {d[2]!r}" if d else f"\n      base: {x!r}\n      site: {y!r}"))

    check("lang", b.html.get("lang") if b.html else None, s.html.get("lang") if s.html else None)
    bt, st = visible_text(b), visible_text(s)
    if bt != st:
        i = next((k for k, (p, q) in enumerate(zip(bt, st)) if p != q), min(len(bt), len(st)))
        problems.append(f"visible text: differs at char {i}\n      base: …{bt[max(0, i-60):i+80]!r}\n      site: …{st[max(0, i-60):i+80]!r}")
    check("title", norm_ws(b.title.get_text()) if b.title else None, norm_ws(s.title.get_text()) if s.title else None)
    check("meta/link", head_items(b), head_items(s))
    check("json-ld", jsonld(b), jsonld(s))
    check("links", apply_exceptions(page, links(b, page)), links(s, page))
    check("images", images(b), images(s))
    check("scripts", scripts(b), scripts(s))
    check("inline scripts", inline_scripts(b), inline_scripts(s))
    check("hooks", hooks(b), hooks(s))
    return problems


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    base, site = Path(sys.argv[1]), Path(sys.argv[2])
    names = pages(base)
    total = 0
    for page in names:
        problems = compare_page(base, site, page)
        total += len(problems)
        print(f"{'OK  ' if not problems else 'FAIL'} {page}")
        for p in problems:
            print(f"    - {p}")
    extra = sorted(set(pages(site)) - set(names))
    for e in extra:
        print(f"FAIL {e}: page exists only in site")
        total += 1
    print(f"\n{len(names)} pages compared, {total} differences")
    used = sorted({k[0] + " " + k[1] + " -> " + v for k, v in EXCEPTIONS.items()})
    print("Tolerated: ?v= cache parameter; " + "; ".join(used))
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
