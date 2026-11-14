#!/usr/bin/env python3
"""items.py — the item numbers a turn names, and whether it lays each out.

Two Stop hooks read a turn's item numbers: hooks/plain.py holds a bare
number, hooks/shown.py a move asking an item it never shows. One reading
serves both, so a range counts each item in it: "items 15 to 21" is seven,
and passes only when all seven are laid out.

Imported, never run.
"""

import re

# "item 55", "items 61 and 62", "items 15 to 21".
NAMED = re.compile(r"\bitems?\s+(\d+(?:\s*(?:,\s*|\s+and\s+|\s+to\s+|–|-)\s*\d+)*)", re.I)


def numbers(group: str) -> list:
    """The item numbers one named group holds, in order. "1 to 4" is four."""
    out, last, span = [], None, False
    for tok in re.findall(r"\d+|to|–|-", group):
        if not tok.isdigit():
            span = True
            continue
        n = int(tok)
        out += range(last + 1, n + 1) if span and last is not None else [n]
        last, span = n, False
    return out


def asked(text: str) -> list:
    """Every item number a text names, once each, in order."""
    return sorted({n for m in NAMED.finditer(text) for n in numbers(m.group(1))})


def laid_out(n: int, text: str) -> bool:
    """The text lays item n out, under its heading: "55 · its title"."""
    return bool(re.search(rf"(?mi)^[\s>*#-]*(?:item\s+)?{n}\s*·", text))
