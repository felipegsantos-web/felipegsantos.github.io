#!/usr/bin/env python3
"""Set /Title, /Author and /Subject in each PDF of documents/publications/ from _data/publications.yml.

  /Title    the work's title, without HTML
  /Author   the authors (the editors for the edited volume) in order, separated by commas
  /Subject  the venue line as shown on the site (English page)

The page content is not touched, and the XMP packet is dropped so that it cannot contradict the document information.
Usage: python3 scripts/pdf_metadata.py [--check]      (--check changes nothing and fails if a /Title does not match its entry; used in CI)
Needs: pypdf, pyyaml.
"""
import re
import sys
from pathlib import Path

import yaml
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject

ROOT = Path(__file__).resolve().parent.parent


def plain(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html)).strip()


def subject(w):
    """The venue line, as _includes/pub-card.html builds it for the English page."""
    if w["type"] in ("article", "profile"):
        if "volume" not in w:
            return f"{w['venue']}, online first."
        issue = f"({w['issue']})" if "issue" in w else ""
        pages = f", {w['pages']}" if "pages" in w else ""
        return f"{w['venue']}, {w['volume']}{issue}{pages}."
    return plain(w["venue"])


def expected(w):
    return {"/Title": plain(w["title"]), "/Author": ", ".join(w["authors"]), "/Subject": subject(w)}


def main():
    check = "--check" in sys.argv
    works = yaml.safe_load((ROOT / "_data/publications.yml").read_text(encoding="utf-8"))
    errors = 0
    for w in works:
        if not w.get("pdf"):
            continue
        path = ROOT / w["pdf"].lstrip("/")
        want = expected(w)
        if check:
            info = PdfReader(path).metadata or {}
            for key, value in want.items():
                if info.get(key) != value:
                    print(f"ERROR {path.name}: {key} is {info.get(key)!r}, expected {value!r}")
                    errors += 1
            continue
        # An incremental update appends the changed objects and leaves the rest of the file byte for byte as it was.
        writer = PdfWriter(path, incremental=True)
        if NameObject("/Metadata") in writer._root_object:
            del writer._root_object[NameObject("/Metadata")]
        writer.add_metadata(want)
        writer.write(path)
        print(f"{path.name}: {want['/Title'][:60]}")
    if check:
        print(f"{len(works)} works checked, {errors} problems")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
