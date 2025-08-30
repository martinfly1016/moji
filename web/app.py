from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
from typing import Optional, List
import re

# 复用本项目的生成器
from kaomoji_generator import (
    generate as gen,
    score_faces,
    score_face,
    KEY2CAT,
    load_samples,
    is_valid_face,
)
from tools import import_samples as imp


def project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


app = FastAPI(title="Kaomoji Generator", version="0.1.0")

# CORS (默认允许所有，亦可用环境变量限定)
allow_origins = os.getenv("CORS_ALLOW_ORIGINS", "*")
origins = [o.strip() for o in allow_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if origins == ["*"] else origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/generate")
def api_generate(
    keywords: Optional[str] = Query(None, description="以空格分隔的关键词；支持中文/日文"),
    n: int = Query(8, ge=1, le=30, description="生成数量，1-30"),
    seed: Optional[int] = Query(None, description="随机种子，可选"),
    lang: str = Query("zh", description="语言：zh 或 ja"),
):
    lang = "ja" if str(lang).lower().startswith("ja") else "zh"
    if not keywords or not str(keywords).strip():
        keywords = "猫 可爱" if lang == "zh" else "猫 かわいい"
    parts = re.split(r"\s+", str(keywords).strip())
    words: List[str] = [w for w in parts if w.strip()]
    samples_path = os.path.join(project_root(), "data", "kaomoji.json")
    faces = gen(words, n=n, seed=seed, samples_path=samples_path)
    scores = score_faces(faces, words)
    items = [{"text": t, "score": int(sc)} for t, sc in zip(faces, scores)]
    return JSONResponse({"keywords": words, "lang": lang, "count": len(items), "items": items, "texts": faces})


@app.get("/api/explore")
def api_explore(
    min_score: int = Query(1, ge=0, le=100, description="计入统计的最小相关度"),
    limit: int = Query(5, ge=1, le=20, description="每个词返回的示例数量"),
):
    samples_path = os.path.join(project_root(), "data", "kaomoji.json")
    samples = load_samples(samples_path)
    results = []

    for word, label in KEY2CAT.items():
        faces = samples.get(label, []) or []
        scored = [(f, score_face(f, [word])) for f in faces]
        scored = [(f, s) for (f, s) in scored if s >= min_score]
        if not scored:
            continue
        scored.sort(key=lambda x: x[1], reverse=True)
        count = len(scored)
        avg = sum(s for _, s in scored) / count if count else 0
        top = [{"text": f, "score": int(s)} for f, s in scored[:limit]]
        results.append({
            "word": word,
            "label": label,
            "count": count,
            "avg_score": int(round(avg)),
            "max_score": int(scored[0][1]),
            "examples": top,
        })

    results.sort(key=lambda r: (r["count"], r["avg_score"], r["max_score"]), reverse=True)
    return JSONResponse({"total": len(results), "items": results})


@app.get("/api/preview")
def api_preview(
    limit: int = Query(10, ge=1, le=50, description="每类展示的样本数"),
    filter_bad: bool = Query(True, description="是否过滤HTML/代码等噪声"),
):
    root = project_root()
    sources_file = os.path.join(root, "data", "sources.txt")
    urls: List[str] = []
    if os.path.isfile(sources_file):
        with open(sources_file, "r", encoding="utf-8") as f:
            for line in f:
                u = line.strip()
                if u and not u.startswith("#"):
                    urls.append(u)
    summary = {}
    total = 0
    for url in urls:
        try:
            txt = imp.fetch(url)
            faces = imp.extract_faces(txt)
            for f in faces:
                n = imp.normalize(f)
                if filter_bad and not is_valid_face(n):
                    continue
                cat = imp.categorize(n)
                arr = summary.setdefault(cat, [])
                if n not in arr:
                    arr.append(n)
                    total += 1
        except Exception:
            # 忽略失败的URL
            continue
    items = []
    for cat, arr in summary.items():
        examples = arr[:limit]
        items.append({"category": cat, "count": len(arr), "examples": examples})
    items.sort(key=lambda x: x["count"], reverse=True)
    return JSONResponse({"total": total, "items": items})


# 静态站点（单页应用）
static_dir = os.path.join(project_root(), "web", "static")
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
