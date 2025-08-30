const kw = document.getElementById('kw');
const num = document.getElementById('num');
const seed = document.getElementById('seed');
const go = document.getElementById('go');
const results = document.getElementById('results');
const statusEl = document.getElementById('status');

function setStatus(msg){ statusEl.textContent = msg || '' }

async function generate(){
  const kws = (kw.value || '猫 可爱').trim();
  const n = Math.max(1, Math.min(30, parseInt(num.value || '8', 10)));
  const s = seed.value ? `&seed=${encodeURIComponent(seed.value)}` : '';
  const url = `/api/generate?keywords=${encodeURIComponent(kws)}&n=${n}${s}`;
  setStatus('生成中…');
  try{
    const res = await fetch(url);
    const data = await res.json();
    render(data.items || []);
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
    emo.textContent = it;
    const btn = document.createElement('div');
    btn.className = 'copy';
    btn.textContent = '复制';
    btn.onclick = async () => {
      try{ await navigator.clipboard.writeText(it); btn.textContent = '已复制'; setTimeout(()=>btn.textContent='复制', 1200);}catch{}
    };
    card.appendChild(emo);
    card.appendChild(btn);
    results.appendChild(card);
  });
}

document.querySelectorAll('.chip').forEach(c => {
  c.addEventListener('click', () => {
    const add = c.getAttribute('data-add');
    const parts = kw.value.trim().split(/\s+/).filter(Boolean);
    if(!parts.includes(add)) parts.push(add);
    kw.value = parts.join(' ');
  })
});

go.addEventListener('click', generate);

// 初始示例
kw.value = '猫 可爱';
generate();
