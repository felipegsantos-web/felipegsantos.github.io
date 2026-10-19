#!/usr/bin/env python3
"""Check the language pairing of the built site.

Usage: python3 scripts/check_hreflang.py [SITE_DIR]   (default: _site)

For every page under en/ and es/:
  * it declares hreflang links for en, es and x-default,
  * its own language link points at its own canonical URL,
  * the other language's page exists in the build and declares this page back
    (hreflang links are reciprocal),
and every en/ page has an es/ counterpart and the other way round.
"""
import sys
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup

SITE_URL = "https://www.felipegsantos.com"


def local(url: str) -> str:
    return urlparse(url).path


def page_info(path: Path):
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    langs = {l.get("hreflang"): l.get("href") for l in soup.find_all("link", rel="alternate") if l.get("hreflang")}
    canon = soup.find("link", rel="canonical")
    return soup.html.get("lang"), canon.get("href") if canon else None, langs


def main():
    site = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
    pages = {}
    for p in sorted(site.rglob("index.html")):
        rel = "/" + p.relative_to(site).parent.as_posix().strip(".") + "/"
        rel = rel.replace("//", "/")
        if rel.startswith(("/en/", "/es/")):
            pages[rel] = page_info(p)
    errors = []
    for url, (lang, canon, alts) in pages.items():
        if lang != url[1:3]:
            errors.append(f"{url}: <html lang={lang!r}> does not match its folder")
        for k in ("en", "es", "x-default"):
            if k not in alts:
                errors.append(f"{url}: missing hreflang={k}")
        if canon != SITE_URL + url:
            errors.append(f"{url}: canonical is {canon!r}")
        if alts.get(lang) != SITE_URL + url:
            errors.append(f"{url}: hreflang={lang} is {alts.get(lang)!r}, expected itself")
        other = "es" if lang == "en" else "en"
        target = local(alts.get(other, ""))
        if target not in pages:
            errors.append(f"{url}: hreflang={other} points to {target!r}, which is not a page of the site")
            continue
        back = pages[target][2].get(lang)
        if back != SITE_URL + url:
            errors.append(f"{url}: {target} does not link back (its hreflang={lang} is {back!r})")
    en = [u for u in pages if u.startswith("/en/")]
    es = [u for u in pages if u.startswith("/es/")]
    if len(en) != len(es):
        errors.append(f"{len(en)} English pages but {len(es)} Spanish pages")
    for e in errors:
        print("ERROR", e)
    print(f"{len(pages)} pages checked, {len(errors)} problems")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
