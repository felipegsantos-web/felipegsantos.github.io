#!/usr/bin/env python3
"""Check _data/pdf_redirects.yml against the built site: every old PDF path is absent from SITE_DIR and every new path exists.
Also checks that each new path is the `pdf` of a publication and that 404.html carries the mapping.

Usage: python3 scripts/check_pdf_redirects.py [SITE_DIR]   (default: _site)
"""
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


def main():
    site = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
    redirects = yaml.safe_load((ROOT / "_data/pdf_redirects.yml").read_text(encoding="utf-8"))
    pubs = yaml.safe_load((ROOT / "_data/publications.yml").read_text(encoding="utf-8"))
    pdfs = {p["pdf"] for p in pubs if p.get("pdf")}
    page_404 = (site / "404.html").read_text(encoding="utf-8")
    errors = []
    for r in redirects:
        if (site / r["old"].lstrip("/")).exists():
            errors.append(f"old path still in the site: {r['old']}")
        if not (site / r["new"].lstrip("/")).is_file():
            errors.append(f"new path missing from the site: {r['new']}")
        if r["new"] not in pdfs:
            errors.append(f"{r['new']} is not the pdf of any publication")
        if r["old"] not in page_404 or r["new"] not in page_404:
            errors.append(f"404.html does not carry {r['old']}")
    for e in errors:
        print("ERROR", e)
    print(f"{len(redirects)} redirects checked, {len(errors)} problems")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
