#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导入/抓取公开绘文字样本，去重并按启发式分类，合并到 data/kaomoji.json。

使用：
  python tools/import_samples.py --sources data/sources.txt --out data/kaomoji.json
"""
import argparse
import json
import os
import re
import sys
import urllib.request
from typing import Dict, List, Set

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(ROOT, "data", "kaomoji.json")
DEFAULT_SOURCES = os.path.join(ROOT, "data", "sources.txt")


def load_json(path: str) -> Dict[str, List[str]]:
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        out: Dict[str, List[str]] = {}
        for k, v in data.items():
            if isinstance(v, list):
                out[k] = [str(x) for x in v]
        return out
    except Exception:
        return {}


def save_json(path: str, data: Dict[str, List[str]]):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "moji-import/0.1"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        raw = resp.read()
        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError:
            return raw.decode("latin-1", errors="ignore")


FACE_HINT = re.compile(r"[()（）ʕʔ╯┻ツω益ᴥಠಥ；;TToO＿_＾^・·｡ﾟ♥♡✧ᵕᵔ]")


def extract_faces(text: str) -> List[str]:
    faces: Set[str] = set()
    # Try JSON
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            for v in data.values():
                if isinstance(v, list):
                    for s in v:
                        if isinstance(s, str):
                            faces.add(s.strip())
        elif isinstance(data, list):
            for s in data:
                if isinstance(s, str):
                    faces.add(s.strip())
        if faces:
            return [x for x in faces if is_face_like(x)]
    except Exception:
        pass

    # Fallback: by lines
    for line in text.splitlines():
        s = line.strip()
        if is_face_like(s):
            faces.add(s)
    # HTML fallback: grab content inside <code> or <li>
    for m in re.finditer(r"<(code|li)[^>]*>(.*?)</\\1>", text, flags=re.S | re.I):
        cand = re.sub(r"<.*?>", "", m.group(2)).strip()
        if is_face_like(cand):
            faces.add(cand)
    return list(faces)


def is_face_like(s: str) -> bool:
    if not s:
        return False
    if len(s) < 2 or len(s) > 60:
        return False
    if s.startswith("#"):
        return False
    return bool(FACE_HINT.search(s))


def categorize(face: str) -> str:
    t = face
    # Cry
    if any(x in t for x in ["T_T", "；；", ";;", "•̥", "꒦", "｡ﾟ", " ﾟ｡", "ಥ", "つД", "ノД", "༎ຶ", "(T", "；_；"]):
        return "cry"
    # Angry
    if any(x in t for x in ["益", "皿", "凸", "╬", "`д´", "ಠ益", "(╯", "#`", "｀Д´"]):
        return "angry"
    # Sleepy
    if any(x in t for x in ["zZ", "Zz", "｡oO", "-_-", "(－_－)"]):
        return "sleepy"
    # Cat
    if "=^" in t or "ฅ" in t or "ᆺ" in t or "ↀ" in t:
        return "cat"
    # Dog
    if "ᴥ" in t or "（U・" in t or "(U･" in t or "∪･" in t:
        return "dog"
    # Happy
    if any(x in t for x in ["＾▽＾", "^_^", "(＾", "≧▽≦", "٩", "(￣", "(⌒", "♪", "✧", "(˶ᵔ"]):
        return "happy"
    return "misc"


def normalize(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", default=DEFAULT_SOURCES, help="包含URL的文本文件，一行一个")
    ap.add_argument("--out", default=DATA_PATH, help="输出JSON路径")
    args = ap.parse_args()

    sources: List[str] = []
    if os.path.isfile(args.sources):
        with open(args.sources, "r", encoding="utf-8") as f:
            for line in f:
                u = line.strip()
                if u and not u.startswith("#"):
                    sources.append(u)

    if not sources:
        print("No sources provided", file=sys.stderr)
        sys.exit(1)

    existing = load_json(args.out)
    merged: Dict[str, List[str]] = {k: v[:] for k, v in existing.items()}
    for k in ["cat", "dog", "cry", "happy", "angry", "sleepy", "misc"]:
        merged.setdefault(k, [])

    seen: Set[str] = set(normalize(x) for xs in merged.values() for x in xs)
    added = 0

    for url in sources:
        try:
            print(f"Fetching: {url}")
            txt = fetch(url)
            faces = extract_faces(txt)
            for f in faces:
                n = normalize(f)
                if n in seen:
                    continue
                cat = categorize(n)
                merged.setdefault(cat, []).append(n)
                seen.add(n)
                added += 1
        except Exception as e:
            print(f"Warn: failed {url}: {e}")

    # 简单截断防止过大；每类最多5000条（可调）
    for k in merged:
        if isinstance(merged[k], list) and len(merged[k]) > 5000:
            merged[k] = merged[k][:5000]

    save_json(args.out, merged)
    print(f"Done. Added {added} new faces. Output: {args.out}")


if __name__ == "__main__":
    main()

