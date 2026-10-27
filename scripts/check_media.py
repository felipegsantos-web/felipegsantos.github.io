#!/usr/bin/env python3
"""Check _data/media.yml: non-empty summary_en / summary_es of exactly one sentence of at most 100 characters with no em or en dashes,
no leftover gloss_en / gloss_es / always_gloss, and `with` only on op-eds. Usage: python3 scripts/check_media.py"""
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
media = yaml.safe_load((ROOT / "_data/media.yml").read_text(encoding="utf-8"))
errors = []
for m in media:
    i = m.get("id", "?")
    for k in ("gloss_en", "gloss_es", "always_gloss"):
        if k in m:
            errors.append(f"{i}: leftover field {k}")
    if "with" in m and m.get("role") != "oped":
        errors.append(f"{i}: `with` is only for op-eds")
    for k in ("summary_en", "summary_es"):
        t = m.get(k)
        if not isinstance(t, str) or not t.strip():
            errors.append(f"{i}: {k} is missing or empty")
            continue
        n = len(re.findall(r"[.?!](?:\s|$)", t))
        if n != 1:
            errors.append(f"{i}: {k} has {n} sentences (exactly 1)")
        if len(t) > 100:
            errors.append(f"{i}: {k} has {len(t)} characters (maximum 100)")
        if re.search(r"[–—]", t):
            errors.append(f"{i}: {k} has an em or en dash")
print(f"{len(media)} media entries checked")
if errors:
    print("\n".join(errors))
    sys.exit(1)
