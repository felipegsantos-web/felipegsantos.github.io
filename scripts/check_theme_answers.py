#!/usr/bin/env python3
"""Check _data/theme-answers.yml: lead paragraphs of 120 to 180 words, 2 or 3 questions of 2 to 4 sentences, every link to a publication of the theme
that is listed in `sources`, no dashes, no excluded vocabulary. Usage: python3 scripts/check_theme_answers.py [--table]"""
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
answers = yaml.safe_load((ROOT / "_data/theme-answers.yml").read_text(encoding="utf-8"))
pubs = {p["id"]: p for p in yaml.safe_load((ROOT / "_data/publications.yml").read_text(encoding="utf-8"))}
themes = [t["slug"] for t in yaml.safe_load((ROOT / "_data/themes.yml").read_text(encoding="utf-8"))]
BANNED = re.compile(r"[–—]|\b(first|leading|pioneering|extrema derecha|derecha radical|radical right)\b", re.I)


def text(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html)).strip()


def sentences(t):
    t = re.sub(r"\b(Santos|Geva|Mikola|Dr|vs|etc)\.", r"\1", t)
    return [s for s in re.split(r"(?<=[.?!])\s+(?=[A-ZÁÉÍÓÚ¿¡<])", t) if s]


errors = []
for slug in themes:
    a = answers[slug]
    theme_pubs = {p for p, v in pubs.items() if slug in v["themes"]}
    texts = []
    for lang in ("en", "es"):
        intro = a[f"intro_{lang}"]
        n = len(text(intro).split())
        if not 120 <= n <= 180:
            errors.append(f"{slug}/{lang}: lead has {n} words")
        texts.append(intro)
        if not 2 <= len(a["questions"]) <= 3:
            errors.append(f"{slug}: {len(a['questions'])} questions")
        for q in a["questions"]:
            ans = q[f"a_{lang}"]
            ns = len(sentences(text(ans)))
            if not 2 <= ns <= 4:
                errors.append(f"{slug}/{lang}: '{q['q_' + lang]}' has {ns} sentences")
            if not q[f"q_{lang}"].endswith("?"):
                errors.append(f"{slug}/{lang}: heading is not a question")
            texts += [ans, q[f"q_{lang}"]]
            for pid in re.findall(r'href="#pub-([^"]+)"', ans):
                if pid not in q["sources"]:
                    errors.append(f"{slug}: link to {pid} not in the sources of '{q['q_en']}'")
    for t in texts:
        for pid in re.findall(r'href="#pub-([^"]+)"', t):
            if pid not in theme_pubs:
                errors.append(f"{slug}: {pid} is not a publication of this theme")
            if pid not in pubs:
                errors.append(f"{slug}: unknown {pid}")
        if BANNED.search(text(t)):
            errors.append(f"{slug}: banned wording in: {text(t)[:60]}")
for e in errors:
    print("ERROR", e)
if "--table" in sys.argv:
    for slug in themes:
        a = answers[slug]
        print(f"| {slug} | lead | " + ", ".join(sorted(set(re.findall(r'#pub-([^"]+)', a['intro_en'])))) + " |")
        for q in a["questions"]:
            print(f"| {slug} | {q['q_en']} | " + ", ".join(q["sources"]) + " |")
print(f"{len(errors)} problems")
sys.exit(1 if errors else 0)
