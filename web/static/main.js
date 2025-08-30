const kw = document.getElementById('kw');
const langSel = document.getElementById('lang');
const num = document.getElementById('num');
const seed = document.getElementById('seed');
const go = document.getElementById('go');
const results = document.getElementById('results');
const statusEl = document.getElementById('status');

function setStatus(msg){ statusEl.textContent = msg || '' }

function getApiBase(){
  const p = new URLSearchParams(location.search);
  const api = p.get('api');
  return api ? api.replace(/\/$/, '') : '';
}

async function generate(){
  const kws = (kw.value || '猫 可爱').trim();
  const n = Math.max(1, Math.min(30, parseInt(num.value || '8', 10)));
  const s = seed.value ? `&seed=${encodeURIComponent(seed.value)}` : '';
  const base = getApiBase();
  const url = `${base}/api/generate?keywords=${encodeURIComponent(kws)}&n=${n}${s}&lang=${encodeURIComponent(langSel.value)}`;
  setStatus('生成中…');
  try{
    const res = await fetch(url);
    const data = await res.json();
    const items = (data.items || []).map(it => typeof it === 'string' ? ({text: it, score: undefined}) : it);
    // 按分值排序（若存在）
    items.sort((a,b) => (b.score||0) - (a.score||0));
    render(items);
    setStatus(`已生成 ${data.count || 0} 个`);
  }catch(e){
    setStatus('生成失败');
  }
}

function render(items){
  results.innerHTML = '';
  items.forEach((it) => {
    const card = document.createElement('div');
    card.className = 'card';
    const emo = document.createElement('div');
    emo.className = 'emo';
    emo.textContent = it.text || it;
    const btn = document.createElement('div');
    btn.className = 'copy';
    btn.textContent = '复制';
    btn.onclick = async () => {
      const text = it.text || it;
      try{ await navigator.clipboard.writeText(text); btn.textContent = '已复制'; setTimeout(()=>btn.textContent='复制', 1200);}catch{}
    };
    const right = document.createElement('div');
    right.style.display = 'flex';
    right.style.flexDirection = 'column';
    right.style.alignItems = 'flex-end';
    if (it.score !== undefined) {
      const sc = document.createElement('div');
      sc.className = 'muted';
      sc.textContent = `相关度 ${it.score}`;
      right.appendChild(sc);
    }
    right.appendChild(btn);
    card.appendChild(emo);
    card.appendChild(right);
    results.appendChild(card);
  });
}

function renderChips(){
  const el = document.getElementById('chips');
  el.innerHTML = '';
  const muted = document.createElement('div');
  muted.className = 'muted';
  muted.textContent = langSel.value === 'ja' ? 'クイック追加:' : '快速添加：';
  el.appendChild(muted);
  const zh = ['猫','狗','哭','可爱','简洁','夸张'];
  const ja = ['猫','犬','泣く','かわいい','シンプル','派手'];
  const arr = langSel.value === 'ja' ? ja : zh;
  arr.forEach(w => {
    const c = document.createElement('div');
    c.className = 'chip';
    c.textContent = w;
    c.addEventListener('click', () => {
      const parts = kw.value.trim().split(/\s+/).filter(Boolean);
      if(!parts.includes(w)) parts.push(w);
      kw.value = parts.join(' ');
    });
    el.appendChild(c);
  });
}

langSel.addEventListener('change', () => {
  kw.placeholder = langSel.value === 'ja' ? 'キーワード例: 猫 かわいい / 犬 シンプル / 泣く 派手' : '输入关键词，如：猫 可爱 / 狗 简洁 / 哭 夸张';
  kw.value = langSel.value === 'ja' ? '猫 かわいい' : '猫 可爱';
  renderChips();
});

go.addEventListener('click', generate);

// 初始示例
kw.value = '猫 可爱';
renderChips();
generate();
