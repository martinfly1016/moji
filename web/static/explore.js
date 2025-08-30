const tbody = document.getElementById('tbody');
const statusEl = document.getElementById('status');
const go = document.getElementById('go');
const limitEl = document.getElementById('limit');
const minEl = document.getElementById('min');

function setStatus(s){ statusEl.textContent = s || '' }

function getApiBase(){
  const p = new URLSearchParams(location.search);
  const api = p.get('api');
  return api ? api.replace(/\/$/, '') : '';
}

async function load(){
  const base = getApiBase();
  const limit = Math.max(1, Math.min(20, parseInt(limitEl.value||'5',10)));
  const min = Math.max(0, Math.min(100, parseInt(minEl.value||'1',10)));
  const url = `${base}/api/explore?limit=${limit}&min_score=${min}`;
  setStatus('加载中…');
  try{
    const res = await fetch(url);
    const data = await res.json();
    render(data.items||[]);
    setStatus(`共 ${data.total||0} 个关键词`);
  }catch(e){
    setStatus('加载失败');
  }
}

function render(items){
  tbody.innerHTML = '';
  items.forEach(it => {
    const tr = document.createElement('tr');
    const tdWord = document.createElement('td'); tdWord.textContent = it.word; tr.appendChild(tdWord);
    const tdLab = document.createElement('td'); tdLab.innerHTML = `<span class="tag">${it.label}</span>`; tr.appendChild(tdLab);
    const tdCnt = document.createElement('td'); tdCnt.textContent = it.count; tr.appendChild(tdCnt);
    const tdAvg = document.createElement('td'); tdAvg.textContent = it.avg_score; tr.appendChild(tdAvg);
    const tdMax = document.createElement('td'); tdMax.textContent = it.max_score; tr.appendChild(tdMax);
    const tdEg = document.createElement('td');
    (it.examples||[]).forEach(ex => {
      const span = document.createElement('span');
      span.className = 'emo';
      span.style.marginRight = '8px';
      span.textContent = `${ex.text}(${ex.score})`;
      tdEg.appendChild(span);
    });
    tr.appendChild(tdEg);
    tbody.appendChild(tr);
  });
}

go.addEventListener('click', load);

load();

