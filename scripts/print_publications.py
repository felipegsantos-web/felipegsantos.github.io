#!/usr/bin/env python3
"""Print the bibliographic fields of every work in _data/publications.yml, to compare with docs/publications-content.md.

Usage: python3 scripts/print_publications.py [PATH]   (default: _data/publications.yml)
"""
import sys
import yaml


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "_data/publications.yml"
    with open(path, encoding="utf-8") as f:
        works = yaml.safe_load(f)
    for i, w in enumerate(works, 1):
        kind = w["type"]
        if kind in ("article", "profile"):
            source = w["venue"]
        else:
            source = w.get("book_title") or w["venue"]
        print(f"{i:2}. [{kind}] {', '.join(w['authors'])}")
        print(f"    {w['year']}  {w['title']}")
        online = f"  (online {w['online']})" if w.get("online") else ""
        print(f"    {source} | vol. {w.get('volume', '-')} | issue {w.get('issue', '-')} | pages {w.get('pages', '-')}{online}")
    print(f"\n{len(works)} works")


if __name__ == "__main__":
    main()
