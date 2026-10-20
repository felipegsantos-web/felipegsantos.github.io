#!/usr/bin/env python3
"""Parse every JSON-LD block of the built site and check it against _data/.

Usage: python3 scripts/check_jsonld.py [SITE_DIR]   (default: _site)

* every block is valid JSON;
* volume, issue and pagination match publications.yml;
* each publication block has the authors (or editors) of publications.yml, in the same order, with Felipe as {"@id": ".../#person"};
* every page, the root page and the 404 page included, defines the Person (@id .../#person) exactly once, with the alternateName list of profile.yml
  (references by @id do not count);
* the media pages (EN and ES) have an ItemList with one item per entry of media.yml, in the same order, with the type, publisher and
  author or mentions that the entry's role calls for.
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


MEDIA_TYPES = {"quoted": "NewsArticle", "guest": "PodcastEpisode", "oped": "OpinionNewsArticle"}


def check_media(block, media):
    """Problems of a media ItemList against media.yml."""
    items = block.get("itemListElement", [])
    if len(items) != len(media) or block.get("numberOfItems") != len(media):
        return [f"ItemList has {len(items)} items (numberOfItems {block.get('numberOfItems')}), media.yml has {len(media)}"]
    errors = []
    for pos, (it, m) in enumerate(zip(items, media), 1):
        node = it.get("item", {})
        want = {
            "@type": MEDIA_TYPES[m["role"]], "headline": m["headline"], "url": m["url"], "datePublished": str(m["date"]),
            "inLanguage": m["language"], "publisher": {"@type": "Organization", "name": m["outlet"]},
        }
        for k, v in want.items():
            if node.get(k) != v:
                errors.append(f"media item {pos} ({m['id']}): {k} is {node.get(k)!r}, expected {v!r}")
        if it.get("position") != pos:
            errors.append(f"media item {pos} ({m['id']}): position {it.get('position')}")
        if m["role"] == "oped":
            authors = [{"@id": PERSON}] + [{"@type": "Person", "name": w} for w in m.get("with", [])]
            if node.get("author") != authors or "mentions" in node:
                errors.append(f"media item {pos} ({m['id']}): author {node.get('author')!r}, expected {authors!r}")
        elif node.get("mentions") != {"@id": PERSON} or "author" in node:
            errors.append(f"media item {pos} ({m['id']}): mentions {node.get('mentions')!r}")
    return errors


def main():
    site = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
    pubs = {p["id"]: p for p in yaml.safe_load((ROOT / "_data/publications.yml").read_text(encoding="utf-8"))}
    profile = yaml.safe_load((ROOT / "_data/profile.yml").read_text(encoding="utf-8"))
    me = {profile["name"], *profile["name_variants"]}
    errors, n_blocks, n_works = [], 0, 0
    media = yaml.safe_load((ROOT / "_data/media.yml").read_text(encoding="utf-8"))
    media_pages = set()
    for path in sorted(site.rglob("*.html")):
        rel = "/" + path.relative_to(site).as_posix()
        try:
            data = blocks(path)
        except json.JSONDecodeError as e:
            errors.append(f"{rel}: invalid JSON-LD ({e})")
            continue
        n_blocks += len(data)
        defs = [n for b in data for n in walk(b) if n.get("@type") == "Person" and n.get("@id") == PERSON]
        if len(defs) != 1:
            errors.append(f"{rel}: the Person is defined {len(defs)} times, expected once")
        elif defs[0].get("alternateName") != profile["name_variants"]:
            errors.append(f"{rel}: the Person's alternateName {defs[0].get('alternateName')!r} does not match profile.yml")
        for b in data:
            if b.get("@type") == "ItemList":
                media_pages.add(rel)
                errors.extend(f"{rel}: {e}" for e in check_media(b, media))
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
            nodes = list(walk(b))
            vol = next((n.get("volumeNumber") for n in nodes if n.get("@type") == "PublicationVolume"), None)
            iss = next((n.get("issueNumber") for n in nodes if n.get("@type") == "PublicationIssue"), None)
            if pub["type"] in ("article", "profile") and (vol, iss) != (
                str(pub["volume"]) if "volume" in pub else None, str(pub["issue"]) if "issue" in pub else None
            ):
                errors.append(f"{rel}: {pub['id']} volume/issue {vol}/{iss} do not match the data")
            if b.get("pagination") != pub.get("pages"):
                errors.append(f"{rel}: {pub['id']} pagination {b.get('pagination')!r} does not match the data")
            if pub.get("isbn_print"):
                got_isbn = b.get("isbn") if b.get("@type") == "Book" else (b.get("isPartOf") or {}).get("isbn")
                if got_isbn != pub["isbn_print"]:
                    errors.append(f"{rel}: {pub['id']} isbn {got_isbn!r} does not match the data")
            same = [u for u in (pub.get("oa_url"), pub.get("pdf") and "https://www.felipegsantos.com" + pub["pdf"]) if u]
            if bool(same) != bool(b.get("isAccessibleForFree")) or (same and b.get("sameAs") != same):
                errors.append(f"{rel}: {pub['id']} open-access fields do not match the data")
    expected = {"/en/media/index.html", "/es/medios/index.html"}
    if media_pages != expected:
        errors.append(f"media ItemList on {sorted(media_pages)}, expected {sorted(expected)}")
    for e in errors:
        print("ERROR", e)
    print(f"{n_blocks} JSON-LD blocks, {n_works} publication blocks checked, {len(errors)} problems")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
