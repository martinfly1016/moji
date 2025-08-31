Kaomoji Generator（绘文字生成器）

概览
- 关键词到类别映射（猫/狗/哭/开心/生气/困）。
- 模板+部件库组合，支持风格偏置（可爱/简洁/夸张等）。
- 可从本地样本库 `data/kaomoji.json` 扩展；后续可接入在线样本。

使用（CLI）
- 运行：`python kaomoji_generator.py 猫 可爱 -n 6`。
- 更多示例：
  - `python kaomoji_generator.py 狗 简洁 -n 6`
  - `python kaomoji_generator.py 哭 夸张 -n 6`
  - 指定随机种子：`--seed 42`

使用（Web）
- 安装依赖：`pip install -r requirements.txt`
- 启动服务：`uvicorn web.app:app --host 0.0.0.0 --port 8000`
- 打开：`http://localhost:8000`（内置静态页面，可直接生成/复制）
- API：`GET /api/generate?keywords=猫 可爱&n=8&seed=42`

语言切换
- Web 页面左侧可选择语言：简体中文／日本語。
- API 亦支持 `lang` 参数：`/api/generate?keywords=猫 かわいい&lang=ja`。
- 日文关键词示例：
  - 类别：`猫 / 犬 / 泣く / 嬉しい / 怒る / 眠い`
  - 风格：`かわいい / シンプル / 派手`

部署到 Vercel（Serverless）
- 在 Vercel 项目设置中将 Root Directory 置为 `moji/`。
- 代码已包含 `vercel.json` 与 `api/index.py`：
  - `api/index.py` 暴露 FastAPI `app`；
  - `vercel.json` 将静态资源与数据文件打包到函数，并将所有路由指向该函数；
- 关联 GitHub 后，推送到 `main` 将自动部署；部署完成后直接访问站点根路径即可。

数据扩展
- 在 `data/kaomoji.json` 里按类别新增样例；生成器会优先以样例做“基模板+轻改”。
- 推荐的公开样本来源（人工确认后再导入）：
  - japaneseemoticons.me（分类齐全，适合人工筛）
  - kaomoji.ru（多语言入口，便于浏览）
  - textfac.es（ASCII/表情集合）
  - “donger list”/“kaomoji list” 相关检索（GitHub 与网页上有不少整理）

导入脚本（可选）
- 抓取/导入：`python tools/import_samples.py --sources data/sources.txt --out data/kaomoji.json`
- 说明：
  - 支持文本/JSON/部分HTML（<code>/<li>）
  - 自动去重并按启发式归类到 cat/dog/cry/happy/angry/sleepy/misc
  - 可编辑 `data/sources.txt` 添加更多来源

GitHub 仓库
- 本地确认运行后，可初始化为仓库并推送到 GitHub。
- 若需我这边代操作：请提供仓库名、公开/私有偏好，以及是否使用 GitHub CLI（`gh`）。

开发
- Python 3.8+
- 单文件 CLI：`kaomoji_generator.py`
- 数据：`data/kaomoji.json`
 - Web：FastAPI at `web/app.py`，静态页面在 `web/static/`
 Kaomoji Generator（绘文字生成器）
