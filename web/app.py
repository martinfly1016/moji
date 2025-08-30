from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
from typing import Optional, List

# 复用本项目的生成器
from kaomoji_generator import generate as gen


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
    keywords: str = Query("猫 可爱", description="以空格分隔的关键词，如: 猫 可爱 / 狗 简洁 / 哭 夸张"),
    n: int = Query(8, ge=1, le=30, description="生成数量，1-30"),
    seed: Optional[int] = Query(None, description="随机种子，可选"),
):
    words: List[str] = [w for w in keywords.split() if w.strip()]
    samples_path = os.path.join(project_root(), "data", "kaomoji.json")
    items = gen(words, n=n, seed=seed, samples_path=samples_path)
    return JSONResponse({"keywords": words, "count": len(items), "items": items})


# 静态站点（单页应用）
static_dir = os.path.join(project_root(), "web", "static")
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
