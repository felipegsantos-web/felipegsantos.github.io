#!/usr/bin/env python3
"""Search visibility checks on the built site.

Usage: python3 scripts/check_visibility.py [SITE_DIR]   (default: _site)

* the other spellings of the name (name_variants in profile.yml) appear in no visible text node, except in publication author lists
  (they are bibliographic data: the names as printed in the work). Attributes, <meta>, <title>, JSON-LD and scripts are not visible text;
* the <meta name="description"> of the homepages and the root page is at most 160 characters;
* llms.txt has the "Also published as" line and one line per entry of publications.yml.
"""
import sys
from pathlib import Path

import yaml
from bs4 import BeautifulSoup, Comment

ROOT = Path(__file__).resolve().parent.parent
HIDDEN = {"script", "style", "title", "head", "noscript", "template"}


def visible_hits(path, variants):
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    hits = []
    for node in soup.find_all(string=True):
        if isinstance(node, Comment) or HIDDEN & {p.name for p in node.parents}:
            continue
        text = " ".join(node.split())
        for v in variants:
            if v in text:
                in_authors = node.find_parent(class_="pub-entry__authors") is not None
                hits.append((v, in_authors, text[:90]))
    return hits


def main():
    site = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
    profile = yaml.safe_load((ROOT / "_data/profile.yml").read_text(encoding="utf-8"))
    pubs = yaml.safe_load((ROOT / "_data/publications.yml").read_text(encoding="utf-8"))
    errors, allowed = [], 0
    for path in sorted(site.rglob("*.html")):
        rel = "/" + path.relative_to(site).as_posix()
        for variant, in_authors, text in visible_hits(path, profile["name_variants"]):
            if in_authors:
                allowed += 1
            else:
                errors.append(f"{rel}: visible text has {variant!r}: {text!r}")
    for rel in ("/index.html", "/en/index.html", "/es/index.html"):
        meta = BeautifulSoup((site / rel.lstrip("/")).read_text(encoding="utf-8"), "html.parser").find("meta", attrs={"name": "description"})
        n = len(meta["content"]) if meta else 0
        if not 0 < n <= 160:
            errors.append(f"{rel}: meta description has {n} characters, expected 1 to 160")
    llms = (site / "llms.txt").read_text(encoding="utf-8")
    also = "Also published as: " + ", ".join(profile["name_variants"]) + "."
    if also not in llms.splitlines():
        errors.append(f"llms.txt lacks the line {also!r}")
    section = llms.split("## Publications\n", 1)[-1].split("\n## ", 1)[0]
    lines = [l for l in section.splitlines() if l.startswith("- ")]
    if len(lines) != len(pubs):
        errors.append(f"llms.txt has {len(lines)} publication lines, publications.yml has {len(pubs)}")
    for e in errors:
        print("ERROR", e)
    print(f"name variants in {allowed} author-list occurrences (allowed), {len(lines)} publication lines in llms.txt, {len(errors)} problems")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
