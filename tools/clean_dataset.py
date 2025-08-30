#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
import sys
from typing import Dict, List, Set

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "kaomoji.json")


def is_valid_face(s: str) -> bool:
    if not s:
        return False
    s = s.strip()
    if len(s) < 2 or len(s) > 60:
        return False
    lower = s.lower()
    bad_tokens = [
        "<div", "</div", "<span", "</span", "<option", "</option", "class=", "style=",
        "font-size", "px", "!important", "</", "<script", "</script", "http://", "https://",
    ]
    if any(tok in lower for tok in bad_tokens):
        return False
    if "<" in s or ">" in s:
        return False
    if "&#" in s or ";" in s and any(k in lower for k in ["td:", "hover", "queue.", "push(", ")};", "{}", "return ", "function ", "var ", "let ", "const "]):
        return False
    if any(ch in s for ch in "{};"):
        return False
    import re
    exceptions = {"chu", "nyan", "nya", "zzz"}
    for m in re.finditer(r"[A-Za-z]{4,}", s):
        if m.group(0).lower() not in exceptions:
            return False
    symbol_hint = "()（）ʕʔ╯┻ツω益ᴥಠಥ；;TToO＿_＾^・·｡ﾟ♥♡✧ᵕᵔ"
    return any(ch in s for ch in symbol_hint)


def main(path: str):
    if not os.path.isfile(path):
        print(f"Not found: {path}")
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    cleaned: Dict[str, List[str]] = {}
    removed = 0
    total = 0
    seen: Set[str] = set()
    for cat, items in data.items():
        cleaned_list: List[str] = []
        for s in items if isinstance(items, list) else []:
            total += 1
            s2 = str(s).strip()
            if not is_valid_face(s2):
                removed += 1
                continue
            if s2 in seen:
                continue
            seen.add(s2)
            cleaned_list.append(s2)
        cleaned[cat] = cleaned_list
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)
    print(f"Cleaned. Kept {sum(len(v) for v in cleaned.values())}/{total}, removed {removed}. -> {path}")


if __name__ == "__main__":
    main(DATA)
