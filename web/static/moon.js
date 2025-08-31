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
function imageToMoon(imageData,{block=4,invert=false,levels=5}={}){
  const chars = ['🌑','🌒','🌓','🌔','🌕'];
  const L = Math.min(levels, chars.length);
  const {width,height,data} = imageData;
  let out = '';
  for(let y=0;y<height;y+=block){
    for(let x=0;x<width;x+=block){
      let acc=0,cnt=0;
      for(let j=0;j<block;j++){
        for(let i=0;i<block;i++){
          if(x+i<width && y+j<height){
            const p=((y+j)*width + (x+i))*4; acc+=toGray(data[p],data[p+1],data[p+2]); cnt++;
          }
        }
      }
      const g = acc/cnt; // 0..255
      let idx = Math.floor(g/256*L);
      if(idx>=L) idx=L-1; if(idx<0) idx=0;
      if(invert) idx = L-1-idx;
      out += chars[idx];
    }
    if(y+block<height) out+='\n';
  }
  return out;
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
    render:$('render'),copy:$('copy'),png:$('png'),download:$('download'),canvas:$('canvas')
  };

  async function generate(){
    const t0=performance.now();
    const cfg={fontSize:parseInt(els.fontSize.value,10),bold:els.bold.checked,letter:parseInt(els.letter.value,10),line:parseInt(els.line.value,10),vertical:els.vertical.checked};
    const img = textToImageData(els.text.value,cfg);
    const moon = imageToMoon(img,{block:parseInt(els.block.value,10),invert:els.invert.checked,levels:5});
    els.out.textContent = moon;
    if(els.png.checked){
      renderMoonToCanvas(moon, els.canvas);
      els.download.disabled=false;
    } else {
      els.canvas.width = 1; els.canvas.height = 1; els.download.disabled=true;
    }
    const ms=Math.round(performance.now()-t0);
    els.meta.textContent = `字符 ${els.text.value.length} · 输出 ${moon.split('\n').length} 行 · ${ms}ms`;
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

