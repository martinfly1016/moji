const limitEl = document.getElementById('limit');
const filterEl = document.getElementById('filter');
const go = document.getElementById('go');
const content = document.getElementById('content');
const statusEl = document.getElementById('status');

function setStatus(s){ statusEl.textContent = s || '' }

function getApiBase(){
  const p = new URLSearchParams(location.search);
  const api = p.get('api');
  return api ? api.replace(/\/$/, '') : '';
}

async function load(){
  const base = getApiBase();
  const limit = Math.max(1, Math.min(50, parseInt(limitEl.value||'10',10)));
  const filter = filterEl.checked ? 'true' : 'false';
  const url = `${base}/api/preview?limit=${limit}&filter_bad=${filter}`;
  setStatus('抓取中…可能需要几秒');
  try{
    const res = await fetch(url);
    const data = await res.json();
    render(data);
    setStatus(`候选共 ${data.total||0} 条，按类别展示`);
  }catch(e){
    setStatus('抓取失败');
  }
}

function render(data){
  content.innerHTML = '';
  (data.items||[]).forEach(cat => {
    const wrap = document.createElement('div');
    wrap.className = 'cat';
    const head = document.createElement('div');
    head.className = 'header';
    const title = document.createElement('div');
    title.innerHTML = `<strong>${cat.category}</strong> <span class="pill">${cat.count}</span>`;
    head.appendChild(title);
    wrap.appendChild(head);
    const grid = document.createElement('div');
    grid.className = 'grid';
    (cat.examples||[]).forEach(t => {
      const card = document.createElement('div');
      card.className = 'card';
      const emo = document.createElement('div');
      emo.className = 'emo';
      emo.textContent = t;
      card.appendChild(emo);
      grid.appendChild(card);
    });
    wrap.appendChild(grid);
    content.appendChild(wrap);
  });
}

go.addEventListener('click', load);
load();

