const $ = (id)=>document.getElementById(id);

// Simple grayscale from RGBA
function toGray(r,g,b){ return 0.299*r + 0.587*g + 0.114*b }

// Draw input text on an offscreen canvas and return ImageData
function textToImageData(text,{fontSize=72,bold=true,letter=0,line=8,vertical=false}={}){
  const scale = 2; // render in high-res then downsample via block mapping
  const fs = fontSize*scale;
  const lh = (fontSize+line)*scale;
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d',{willReadFrequently:true});
  ctx.fillStyle = '#000';
  // rough width/height estimation
  const lines = String(text).split(/\n/);
  if(!vertical){
    const family = "'Noto Sans JP', 'Noto Sans SC', system-ui, sans-serif";
    ctx.font = `${bold?'700':'400'} ${fs}px ${family}`;
    let maxW = 0;
    for(const lineText of lines){
      // letter spacing by measuring per char
      let w = 0; for(const ch of lineText){ w += ctx.measureText(ch).width + letter*scale }
      maxW = Math.max(maxW, w);
    }
    canvas.width = Math.ceil(maxW+fs);
    canvas.height = Math.ceil(lh*lines.length + fs*0.5);
    ctx.fillStyle = '#000'; ctx.fillRect(0,0,canvas.width,canvas.height);
    ctx.fillStyle = '#fff'; ctx.font = `${bold?'700':'400'} ${fs}px ${family}`; ctx.textBaseline='top';
    lines.forEach((t,i)=>{
      let x = 0; const y = i*lh;
      for(const ch of t){
        ctx.fillText(ch,x,y); x += ctx.measureText(ch).width + letter*scale;
      }
    });
  }else{
    // simple vertical layout: draw characters in a single column per line
    const family = "'Noto Sans JP', 'Noto Sans SC', system-ui, sans-serif";
    ctx.font = `${bold?'700':'400'} ${fs}px ${family}`;
    let cols = lines.length; // treat each input line as a column
    let maxRows = Math.max(...lines.map(s=>s.length));
    canvas.width = Math.ceil(cols * (fs + letter*scale) + fs);
    canvas.height = Math.ceil(maxRows * lh + fs*0.5);
    ctx.fillStyle = '#000'; ctx.fillRect(0,0,canvas.width,canvas.height);
    ctx.fillStyle = '#fff'; ctx.font = `${bold?'700':'400'} ${fs}px ${family}`; ctx.textBaseline='top';
    lines.forEach((t,ci)=>{
      for(let ri=0;ri<t.length;ri++){
        const x = ci*(fs+letter*scale);
        const y = ri*lh;
        ctx.fillText(t[ri],x,y);
      }
    });
  }
  return ctx.getImageData(0,0,canvas.width,canvas.height);
}

// Map image to moon-emoji mosaic
function imageToMoon(imageData,{block=4,invert=false,levels=5,trim=true}={}){
  const chars = ['🌑','🌒','🌓','🌔','🌕'];
  const L = Math.max(3, Math.min(levels, chars.length));
  const {width,height,data} = imageData;
  const bw = Math.ceil(width/block), bh = Math.ceil(height/block);
  // 1) compute block grayscale (0..L-1 float space)
  const grid = Array.from({length:bh},()=>Array(bw).fill(0));
  for(let by=0; by<bh; by++){
    for(let bx=0; bx<bw; bx++){
      let acc=0,cnt=0;
      for(let j=0;j<block;j++){
        for(let i=0;i<block;i++){
          const x=bx*block+i, y=by*block+j;
          if(x<width && y<height){ const p=(y*width+x)*4; acc+=toGray(data[p],data[p+1],data[p+2]); cnt++; }
        }
      }
      const g = cnt?acc/cnt:0; // 0..255
      grid[by][bx] = (g/255)*(L-1); // map to 0..L-1 float
    }
  }
  // 2) Floyd–Steinberg dithering on block grid for smoother edges
  for(let y=0;y<bh;y++){
    for(let x=0;x<bw;x++){
      const old = grid[y][x];
      const newV = Math.round(old);
      const err = old - newV;
      grid[y][x] = newV;
      if(x+1<bw) grid[y][x+1] += err*7/16;
      if(y+1<bh && x>0) grid[y+1][x-1] += err*3/16;
      if(y+1<bh) grid[y+1][x] += err*5/16;
      if(y+1<bh && x+1<bw) grid[y+1][x+1] += err*1/16;
    }
  }
  // 3) map to emoji index and optionally trim background edge
  const bgIdx = invert ? (L-1) : 0;
  const idxGrid = grid.map(row=>row.map(v=>{
    let idx = Math.max(0, Math.min(L-1, Math.round(v)));
    return invert? (L-1-idx) : idx;
  }));
  let top=0,bottom=bh-1,left=0,right=bw-1;
  if(trim){
    while(top<=bottom && idxGrid[top].every(x=>x===bgIdx)) top++;
    while(bottom>=top && idxGrid[bottom].every(x=>x===bgIdx)) bottom--;
    while(left<=right && idxGrid.every(row=>row[left]===bgIdx)) left++;
    while(right>=left && idxGrid.every(row=>row[right]===bgIdx)) right--;
    if(top>bottom || left>right){ top=0;bottom=-1;left=0;right=-1; }
  }
  const lines=[];
  for(let y=top; y<=bottom; y++){
    let s='';
    for(let x=left; x<=right; x++) s+=chars[idxGrid[y][x]];
    lines.push(s);
  }
  return {text: lines.join('\n'), lines};
}

// Draw moon text back into a PNG for preview
function renderMoonToCanvas(text, canvas){
  const ctx = canvas.getContext('2d');
  const lines = text.split('\n');
  const size = 28; // emoji size
  const pad = 8; const family="system-ui, 'Apple Color Emoji','Segoe UI Emoji','Noto Color Emoji'";
  // measure width by line length * size (emoji roughly square), safe padding
  const w = Math.max(1, ...lines.map(l=>l.length))*size + pad*2;
  const h = lines.length*size + pad*2;
  canvas.width=w; canvas.height=h; ctx.fillStyle='#0b0f14'; ctx.fillRect(0,0,w,h);
  ctx.font = `${size}px ${family}`; ctx.textBaseline='top'; ctx.fillStyle='#ffffff';
  for(let i=0;i<lines.length;i++){
    ctx.fillText(lines[i], pad, pad + i*size);
  }
}

async function main(){
  const els={
    text:$('text'),fontSize:$('fontSize'),bold:$('bold'),letter:$('letter'),line:$('line'),
    block:$('block'),invert:$('invert'),vertical:$('vertical'),out:$('out'),meta:$('meta'),
    render:$('render'),copy:$('copy'),png:$('png'),download:$('download'),canvas:$('canvas'),
    trim:$('trim'),levels:$('levels')
  };

  async function generate(){
    const t0=performance.now();
    const cfg={fontSize:parseInt(els.fontSize.value,10),bold:els.bold.checked,letter:parseInt(els.letter.value,10),line:parseInt(els.line.value,10),vertical:els.vertical.checked};
    const img = textToImageData(els.text.value,cfg);
    const res = imageToMoon(img,{block:parseInt(els.block.value,10),invert:els.invert.checked,levels:parseInt(els.levels.value,10)||5,trim:els.trim.checked});
    els.out.textContent = res.text;
    if(els.png.checked){
      renderMoonToCanvas(res.text, els.canvas);
      els.download.disabled=false;
    } else {
      els.canvas.width = 1; els.canvas.height = 1; els.download.disabled=true;
    }
    const ms=Math.round(performance.now()-t0);
    els.meta.textContent = `字符 ${els.text.value.length} · 输出 ${res.lines.length} 行 · ${ms}ms`;
  }

  $('download').addEventListener('click',()=>{
    const a=document.createElement('a'); a.download='moon-emoji.png'; a.href=els.canvas.toDataURL('image/png'); a.click();
  });
  $('copy').addEventListener('click',async()=>{ try{ await navigator.clipboard.writeText(els.out.textContent||''); $('copy').textContent='已复制'; setTimeout(()=>$('copy').textContent='复制文本',1200);}catch{} });
  $('render').addEventListener('click',generate);

  // Auto-generate on first load
  generate();
}

main();
