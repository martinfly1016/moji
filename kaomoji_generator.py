#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import json
import os
import random
from typing import List, Dict, Callable

# 关键词到类别
KEY2CAT = {
    "猫": "cat", "喵": "cat", "小猫": "cat",
    "狗": "dog", "汪": "dog", "小狗": "dog",
    "哭": "cry", "难过": "cry", "伤心": "cry", "委屈": "cry", "呜呜": "cry",
    "开心": "happy", "高兴": "happy", "笑": "happy",
    "生气": "angry", "愤怒": "angry", "凶": "angry",
    "困": "sleepy", "困了": "sleepy", "累": "sleepy", "疲惫": "sleepy",
    "可爱": "cute", "卖萌": "cute", "萌": "cute",
}

# 通用装饰与部件库
DECOR = ["♡", "♥", "♪", "✧", "★", "☆", "｡", "❀", "❁", "❣", "彡"]
PAWS = ["ฅ", "ʢ", "ʡ", "ノ", "∠", "o", "੭", "っ"]
WRAPS = [("(", ")"), ("（", "）"), ("ʕ", "ʔ"), ("〈", "〉")]

PARTS: Dict[str, Dict[str, List[str]]] = {
    "cat": {
        "eyes": ["^", "･", "•", "˶", "´", "=", "ꈍ", "ᵔ", "˘"],
        "mouth": ["ω", " ᴥ ", "ᗝ", "﹏", "⌓", "△", "_", "×"],
        "whisker": ["=", "≡"],
        "paws": PAWS,
        "decor": DECOR + ["にゃ", "~"],
    },
    "dog": {
        "eyes": ["ᵔ", "•", "˘", "＾", "꒳", "ᴗ", "ᴖ"],
        "nose": ["ᴥ", "ܫ", "⩊", "ᗣ"],
        "ears": ["U", "▼", "∪", "ʋ", "ᑌ"],
        "decor": DECOR,
    },
    "cry": {
        "eyes": ["˃", "ᵕ", "T", "ಥ", "ó", ";", "•̥", "´", "`", "⌓"],
        "mouth": ["ᗝ", "△", "_", "﹏", "×", "o", "ᵕ"],
        "tear": ["৹", "꒦", "｡ﾟ", " ﾟ｡", "˃̥", "ᵕ̥"],
        "outer": ["๐·°", "°·๐", "｡ﾟ", "ﾟ｡", "°彡", "彡°"],
        "decor": ["…", "~", " "],
    },
    "happy": {
        "eyes": ["^", "・", "•", "˶", "´", "`", "ᵔ", "≧", "✧"],
        "mouth": ["ω", "▽", "ヮ", "ᴗ", "v", "∀", "ㅅ"],
        "decor": DECOR + ["~♪"],
    },
    "angry": {
        "eyes": ["`", "ˋ", "ಠ", "థ", "≧", "•"],
        "mouth": ["皿", "^", "へ", "益", "︿"],
        "vein": ["╬", "凸", "彡", "ᕙ", "ノ", "(#)"],
        "decor": ["!", "!!", "!!!"],
    },
    "sleepy": {
        "eyes": ["-", "﹃", "﹂", "ᴗ", "_", "ᵕ"],
        "mouth": ["_", "﹏", "o", "ᵕ", "ω"],
        "bubble": ["zZ", "Zz", "Zzz", "｡oO"],
        "decor": ["~"],
    },
}


def pick(lst: List[str]):
    return random.choice(lst)


def bias(parts: Dict[str, List[str]], styles: List[str]) -> Dict[str, List[str]]:
    out = {k: v[:] for k, v in parts.items()}
    if any(s in styles for s in ["可爱", "卖萌", "萌"]):
        for key in out:
            out[key] = [x for x in out[key] if any(c in x for c in ["ω", "ᵕ", "ᵔ", "♡", "♥", "✧", "･", "•", "▽", "∀"])] or out[key]
    if any(s in styles for s in ["简洁", "极简", "高冷"]):
        for key in out:
            out[key] = [x for x in out[key] if all(c not in x for c in ["♡", "♥", "✧", "♪", "彡", "｡", "ﾟ", "~"])] or out[key]
    if any(s in styles for s in ["夸张", "浮夸"]):
        for key in out:
            out[key] = out[key] + out[key]
    return out


def gen_cat(styles: List[str]) -> str:
    p = bias(PARTS["cat"], styles)
    L, R = random.choice(WRAPS)
    t = random.choice(["whisker_ears", "paws_round", "paws_tail"])
    if t == "whisker_ears":
        w = pick(p["whisker"])
        e = pick(p["eyes"])
        m = pick(p["mouth"])
        return f"{L}{w}{e}･{m}･{e}{w}{R}"
    if t == "paws_round":
        e = pick(p["eyes"]) ; m = pick(p["mouth"]) ; paw = pick(p["paws"]) ; dec = random.choice(["", pick(p["decor"])])
        return f"{paw}{L}{e}{m}{e}{R}{paw}{dec}"
    e = pick(p["eyes"]) ; m = pick(p["mouth"]) ; paw = pick(p["paws"]) ; dec = random.choice(["♡", "♥", "", ""]) 
    return f"{paw}^{e}{m}{e}^{paw}{dec}"


def gen_dog(styles: List[str]) -> str:
    p = bias(PARTS["dog"], styles)
    L, R = random.choice(WRAPS)
    t = random.choice(["ears_nose", "round_face"])
    if t == "ears_nose":
        ear = pick(p["ears"]) ; nose = pick(p["nose"]) ; mid = random.choice(["・", "·", " "])
        return f"{L}{ear}{mid}{nose}{mid}{ear}{R}"
    eye = pick(p["eyes"]) ; nose = pick(p["nose"]) ; return f"{L}{eye}{nose}{eye}{R}"


def gen_cry(styles: List[str]) -> str:
    p = bias(PARTS["cry"], styles)
    L, R = random.choice(WRAPS)
    t = random.choice(["outer_tears", "inner_tears"])
    if t == "outer_tears":
        outer = pick(p["outer"]) ; el = pick(p["eyes"]) ; er = pick(p["eyes"]) ; m = pick(p["mouth"]) ; tl = pick(p["tear"]) ; tr = pick(p["tear"]) 
        return f"{outer}{L}{tl}{el}{m}{er}{tr}{R}{outer}"
    m = pick(p["mouth"]) ; return f"{L} ´•̥{m}•̥ {R}"


def gen_happy(styles: List[str]) -> str:
    p = bias(PARTS["happy"], styles)
    L, R = random.choice(WRAPS)
    e = pick(p["eyes"]) ; m = pick(p["mouth"]) ; dec = random.choice(["", pick(p["decor"])])
    return f"{L}{e}{m}{e}{R}{dec}"


def gen_angry(styles: List[str]) -> str:
    p = bias(PARTS["angry"], styles)
    L, R = random.choice(WRAPS)
    v = random.choice(p["vein"]) ; e = pick(p["eyes"]) ; m = pick(p["mouth"]) ; d = pick(p["decor"]) 
    return f"{v}{L}{e}{m}{e}{R}{d}"


def gen_sleepy(styles: List[str]) -> str:
    p = bias(PARTS["sleepy"], styles)
    L, R = random.choice(WRAPS)
    e = pick(p["eyes"]) ; m = pick(p["mouth"]) ; bub = random.choice(p["bubble"])
    return f"{L}{e}{m}{e}{R} {bub}"


GEN: Dict[str, Callable[[List[str]], str]] = {
    "cat": gen_cat, "dog": gen_dog, "cry": gen_cry,
    "happy": gen_happy, "angry": gen_angry, "sleepy": gen_sleepy,
}


def to_category(words: List[str]) -> str:
    for w in words:
        if KEY2CAT.get(w) in GEN:
            return KEY2CAT[w]
    return "happy"


def load_samples(path: str) -> Dict[str, List[str]]:
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # 规范化为 {cat: [str,...]}
        out: Dict[str, List[str]] = {}
        for cat, items in data.items():
            if isinstance(items, list):
                out[cat] = [str(x) for x in items]
        return out
    except Exception:
        return {}


def mutate_from_sample(sample: str) -> str:
    # 轻改：随机替换部分常见部件
    swaps = {
        "ω": ["ᵕ", "ᴗ", "▽"],
        "ᴥ": ["ᗝ", "⩊"],
        "·": ["・", " "],
        "^": ["ᵔ", "˘", "・"],
        "・": ["·", "^"],
        "_": ["﹏", "o"],
        "♡": ["♥", "✧", ""],
    }
    s = list(sample)
    for i, ch in enumerate(s):
        if ch in swaps and random.random() < 0.35:
            s[i] = random.choice(swaps[ch])
    return "".join(s)


def generate(keywords: List[str], n: int = 6, seed: int = None, samples_path: str = "data/kaomoji.json") -> List[str]:
    if seed is not None:
        random.seed(seed)
    cat = to_category(keywords)
    styles = [w for w in keywords if w in ("可爱", "卖萌", "萌", "简洁", "极简", "高冷", "夸张", "浮夸")]
    fn = GEN.get(cat, gen_happy)

    # 样本优先：从近似类别样本做轻改
    samples = load_samples(samples_path)
    pool: List[str] = []
    if cat in samples and samples[cat]:
        base = random.sample(samples[cat], min(len(samples[cat]), max(4, n)))
        pool.extend([mutate_from_sample(b) for b in base])

    # 模板补齐
    seen = set(pool)
    while len(pool) < n:
        s = fn(styles)
        if s not in seen:
            seen.add(s)
            pool.append(s)
    return pool[:n]


def main():
    ap = argparse.ArgumentParser(description="Kaomoji Generator")
    ap.add_argument("keywords", nargs="*", help="如: 猫 可爱 / 狗 简洁 / 哭 夸张")
    ap.add_argument("-n", type=int, default=6, help="生成数量")
    ap.add_argument("--seed", type=int, default=None, help="随机种子")
    ap.add_argument("--samples", default="data/kaomoji.json", help="样本库路径(JSON)")
    args = ap.parse_args()
    kws = args.keywords if args.keywords else ["猫", "可爱"]
    for s in generate(kws, n=args.n, seed=args.seed, samples_path=args.samples):
        print(s)


if __name__ == "__main__":
    main()
