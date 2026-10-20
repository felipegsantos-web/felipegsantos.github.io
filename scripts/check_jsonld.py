#!/usr/bin/env python3
"""Parse every JSON-LD block of the built site and check it against _data/.

Usage: python3 scripts/check_jsonld.py [SITE_DIR]   (default: _site)

* every block is valid JSON;
* each publication block has the authors (or editors) of publications.yml, in the same order, with Felipe as {"@id": ".../#person"};
* the Person is defined at most once per page (references by @id do not count);
* the homepages and CV pages (EN and ES) define it exactly once, and no other page does.
"""
import json
import re
import sys
from pathlib import Path

import yaml
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
PERSON = "https://www.felipegsantos.com/#person"


def blocks(path):
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    return [json.loads(s.string) for s in soup.find_all("script", type="application/ld+json")]


def walk(node):
    if isinstance(node, dict):
        yield node
        for v in node.values():
            yield from walk(v)
    elif isinstance(node, list):
        for v in node:
            yield from walk(v)


def main():
    site = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
    pubs = {p["id"]: p for p in yaml.safe_load((ROOT / "_data/publications.yml").read_text(encoding="utf-8"))}
    profile = yaml.safe_load((ROOT / "_data/profile.yml").read_text(encoding="utf-8"))
    me = {profile["name"], *profile["name_variants"]}
    errors, n_blocks, n_works = [], 0, 0
    person_pages = set()
    for path in sorted(site.rglob("*.html")):
        rel = "/" + path.relative_to(site).as_posix()
        try:
            data = blocks(path)
        except json.JSONDecodeError as e:
            errors.append(f"{rel}: invalid JSON-LD ({e})")
            continue
        n_blocks += len(data)
        defs = [n for b in data for n in walk(b) if n.get("@type") == "Person" and n.get("@id") == PERSON]
        if len(defs) > 1:
            errors.append(f"{rel}: the Person is defined {len(defs)} times")
        if defs:
            person_pages.add(rel)
        for b in data:
            m = re.match(r"https://www\.felipegsantos\.com/#work-(.+)", b.get("@id", ""))
            if not m:
                continue
            n_works += 1
            pub = pubs.get(m.group(1))
            if pub is None:
                errors.append(f"{rel}: unknown work {m.group(1)}")
                continue
            got = b.get("author") or b.get("editor")
            want = pub["authors"]
            if len(got) != len(want):
                errors.append(f"{rel}: {pub['id']} has {len(got)} authors, data has {len(want)}")
                continue
            for g, w in zip(got, want):
                ok = g == {"@id": PERSON} if w in me else g.get("name") == w and g.get("@type") == "Person"
                if not ok:
                    errors.append(f"{rel}: {pub['id']} author {g!r} does not match {w!r}")
            same = [u for u in (pub.get("oa_url"), pub.get("pdf") and "https://www.felipegsantos.com" + pub["pdf"]) if u]
            if bool(same) != bool(b.get("isAccessibleForFree")) or (same and b.get("sameAs") != same):
                errors.append(f"{rel}: {pub['id']} open-access fields do not match the data")
    expected = {"/en/index.html", "/es/index.html", "/en/cv/index.html", "/es/cv/index.html"}
    if person_pages != expected:
        errors.append(f"Person defined on {sorted(person_pages)}, expected {sorted(expected)}")
    for e in errors:
        print("ERROR", e)
    print(f"{n_blocks} JSON-LD blocks, {n_works} publication blocks checked, {len(errors)} problems")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
