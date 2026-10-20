#!/usr/bin/env python3
"""Check the open-access links in _data/publications.yml.

Usage: python3 scripts/check_oa_links.py   (needs network and `pdftotext`; not part of CI)

For every entry with an `oa_url` it reports: the HTTP status, whether the response is a PDF,
and whether the first two pages of the PDF contains the opening words of the work's title.
City Research Online is rate limited for bots, so requests are spaced out.
"""
import re
import subprocess
import sys
import tempfile
import time
import unicodedata
import urllib.request
from pathlib import Path

import yaml

DATA = Path(__file__).resolve().parent.parent / "_data" / "publications.yml"
UA = "Mozilla/5.0 (X11; Linux x86_64) felipegsantos.com link check"


def norm(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text).replace("\u2019", "").replace("'", "")
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def main() -> int:
    pubs = yaml.safe_load(DATA.read_text(encoding="utf-8"))
    bad = 0
    for p in pubs:
        url = p.get("oa_url")
        if not url:
            continue
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                body, ctype, status = r.read(), r.headers.get("content-type", ""), r.status
        except Exception as e:  # noqa: BLE001
            print(f"FAIL {p['id']}: {e}")
            bad += 1
            continue
        is_pdf = body[:5] == b"%PDF-"
        title_ok = False
        if is_pdf:
            with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
                f.write(body)
                f.flush()
                text = subprocess.run(["pdftotext", "-l", "2", f.name, "-"], capture_output=True, text=True).stdout
            words = norm(p["title"]).split()[:6]
            title_ok = norm(" ".join(words)) in norm(text)
        ok = status == 200 and is_pdf and title_ok
        bad += not ok
        print(f"{'OK  ' if ok else 'FAIL'} {p['id']}: {status} {ctype.split(';')[0]} pdf={is_pdf} title={title_ok} version={p.get('oa_version')}")
        time.sleep(2)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
