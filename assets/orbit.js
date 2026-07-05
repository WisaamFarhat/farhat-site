// Orbital scene. Full-hero background: Earth limb, the geostationary arc with real
// filings plotted at their longitudes, longitude ticks, starfield, and moving NGSO craft.
(function(){
  const canvas = document.getElementById('orbit-canvas');
  if(!canvas) return;
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const ctx = canvas.getContext('2d');
  let W,H,DPR,geom;

  const filings = (window.ORBIT_FILINGS||[]).filter(f=>typeof f.deg==='number');
  const gso = filings.filter(f=>f.type==='GSO');

  // starfield
  const stars = Array.from({length:150},()=>({
    x:Math.random(), y:Math.random(), r:Math.random()*1.3+.25,
    tw:Math.random()*Math.PI*2, sp:.5+Math.random()*1.6
  }));

  // NGSO movers: shallow crossing arcs, varied speed/direction
  const movers = [
    {p:Math.random(), sp:.00042, y:.30, amp:.05, dir: 1},
    {p:Math.random(), sp:.00030, y:.44, amp:.08, dir:-1},
    {p:Math.random(), sp:.00055, y:.22, amp:.04, dir: 1},
  ];

  function resize(){
    DPR = Math.min(window.devicePixelRatio||1, 2);
    W = canvas.clientWidth; H = canvas.clientHeight;
    canvas.width = W*DPR; canvas.height = H*DPR;
    ctx.setTransform(DPR,0,0,DPR,0,0);
    const R = Math.max(W*0.85, 640);
    geom = { cx: W/2, R, apexY: H*0.60, cy: H*0.60 + R,
             a0: Math.PI*1.30, a1: Math.PI*1.70,     // visible arc span
             limbR: Math.max(W*1.05, 800) };
    geom.limbCy = H*0.965 + geom.limbR;              // Earth limb top edge ~ bottom of hero
  }

  function arcPoint(deg){ // longitude -180..180 -> point on GSO arc
    const frac = (deg + 180) / 360;
    const a = geom.a0 + frac * (geom.a1 - geom.a0);
    return { x: geom.cx + geom.R*Math.cos(a), y: geom.cy + geom.R*Math.sin(a), a };
  }

  let t = 0, raf;
  function draw(){
    t += reduce ? 0 : 1;
    ctx.clearRect(0,0,W,H);

    // — stars (twinkle) —
    for(const s of stars){
      const a = .22 + .5*Math.abs(Math.sin(s.tw + t*.02*s.sp));
      ctx.fillStyle = `rgba(216,205,187,${a*.6})`;
      ctx.beginPath(); ctx.arc(s.x*W, s.y*H, s.r, 0, 7); ctx.fill();
    }

    // — Earth limb: glowing planet edge along the bottom —
    ctx.save();
    ctx.strokeStyle = 'rgba(196,168,130,.55)';
    ctx.lineWidth = 1.6;
    ctx.shadowColor = 'rgba(196,168,130,.8)';
    ctx.shadowBlur = 26;
    ctx.beginPath(); ctx.arc(geom.cx, geom.limbCy, geom.limbR, Math.PI*1.32, Math.PI*1.68); ctx.stroke();
    ctx.restore();
    // atmosphere haze above the limb
    const hz = ctx.createLinearGradient(0, H*0.86, 0, H);
    hz.addColorStop(0,'rgba(196,168,130,0)');
    hz.addColorStop(1,'rgba(196,168,130,.10)');
    ctx.fillStyle = hz; ctx.fillRect(0, H*0.86, W, H*0.14);

    // — GSO arc (double line) —
    ctx.strokeStyle = 'rgba(196,168,130,.34)'; ctx.lineWidth = 1.2;
    ctx.beginPath(); ctx.arc(geom.cx, geom.cy, geom.R, geom.a0, geom.a1); ctx.stroke();
    ctx.strokeStyle = 'rgba(196,168,130,.10)';
    ctx.beginPath(); ctx.arc(geom.cx, geom.cy, geom.R-10, geom.a0, geom.a1); ctx.stroke();

    // — longitude ticks + labels every 60 degrees —
    ctx.font = '9px "JetBrains Mono", monospace';
    ctx.textAlign = 'center';
    for(let d=-120; d<=120; d+=60){
      const p = arcPoint(d);
      const nx = (p.x-geom.cx)/geom.R, ny = (p.y-geom.cy)/geom.R;
      ctx.strokeStyle = 'rgba(196,168,130,.35)'; ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(p.x - nx*5, p.y - ny*5);
      ctx.lineTo(p.x + nx*5, p.y + ny*5);
      ctx.stroke();
      const lbl = d===0 ? '0\u00B0' : (Math.abs(d) + '\u00B0' + (d>0?'E':'W'));
      ctx.fillStyle = 'rgba(196,168,130,.38)';
      ctx.fillText(lbl, p.x, p.y + 16);
    }

    // — GSO filings at their true longitudes —
    gso.forEach((f,i)=>{
      const p = arcPoint(f.deg);
      const pulse = 1 + .35*Math.sin(t*.05 + i*1.7);
      const g = ctx.createRadialGradient(p.x,p.y,0,p.x,p.y,9*pulse);
      g.addColorStop(0,'rgba(232,220,196,.95)'); g.addColorStop(1,'rgba(232,220,196,0)');
      ctx.fillStyle = g; ctx.beginPath(); ctx.arc(p.x,p.y,9*pulse,0,7); ctx.fill();
      ctx.fillStyle = '#E8DCC4';
      ctx.beginPath(); ctx.arc(p.x,p.y,2.2,0,7); ctx.fill();
    });

    // labels for the three biggest filings, kept to the right half so they
    // never sit under the hero text
    ctx.textAlign = 'left';
    ctx.font = '10px "JetBrains Mono", monospace';
    let labeled = 0;
    for(const f of gso){
      if(labeled >= 3) break;
      const p = arcPoint(f.deg);
      if(p.x < W*0.52 || p.y < 30) continue;
      ctx.strokeStyle = 'rgba(216,205,187,.30)'; ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(p.x, p.y-6); ctx.lineTo(p.x+10, p.y-22); ctx.lineTo(p.x+16, p.y-22); ctx.stroke();
      ctx.fillStyle = 'rgba(232,220,196,.78)';
      ctx.fillText(f.name, p.x+20, p.y-19);
      labeled++;
    }

    // — NGSO movers with trails —
    for(const m of movers){
      m.p = (m.p + (reduce?0:m.sp*m.dir) + 1) % 1;
      const px = m.p * (W+160) - 80;
      const py = H*m.y + Math.sin(m.p*Math.PI*2)*H*m.amp;
      // trail
      const tg = ctx.createLinearGradient(px - 46*m.dir, py, px, py);
      tg.addColorStop(0,'rgba(192,136,41,0)'); tg.addColorStop(1,'rgba(192,136,41,.5)');
      ctx.strokeStyle = tg; ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(px - 46*m.dir, py + 6*m.dir); ctx.lineTo(px, py); ctx.stroke();
      ctx.fillStyle = '#C08829';
      ctx.beginPath(); ctx.arc(px, py, 1.8, 0, 7); ctx.fill();
    }

    if(!reduce) raf = requestAnimationFrame(draw);
  }

  function start(){ resize(); draw(); }
  window.addEventListener('resize', ()=>{ resize(); if(reduce){ ctx.clearRect(0,0,W,H); draw(); } });
  // The stylesheet may not have laid out the hero when this script first runs,
  // leaving the canvas at its 300x150 default. Re-measure once everything loads,
  // and watch for later size changes.
  window.addEventListener('load', ()=>{ resize(); if(reduce){ ctx.clearRect(0,0,W,H); draw(); } });
  if('ResizeObserver' in window){
    new ResizeObserver(()=>{ resize(); if(reduce){ ctx.clearRect(0,0,W,H); draw(); } }).observe(canvas);
  }
  start();
})();

// Scroll reveals (IntersectionObserver, no library needed, GitHub Pages friendly)
(function(){
  const els = document.querySelectorAll('.reveal');
  if(!('IntersectionObserver' in window)){ els.forEach(e=>e.classList.add('in')); return; }
  const io = new IntersectionObserver((entries)=>{
    entries.forEach((e,i)=>{ if(e.isIntersecting){ setTimeout(()=>e.target.classList.add('in'), i*60); io.unobserve(e.target);} });
  },{threshold:.12, rootMargin:'0px 0px -8% 0px'});
  els.forEach(e=>io.observe(e));
})();

// animated reach bars on filing tables
(function(){
  document.querySelectorAll('.reachbar').forEach(b=>{
    const w = b.getAttribute('data-w')||'0';
    setTimeout(()=>{ b.style.width = w+'px'; }, 300);
  });
})();

// Safety net: ensure all reveals become visible even without observer/scroll
window.addEventListener('load', function(){
  setTimeout(function(){
    document.querySelectorAll('.reveal:not(.in)').forEach(function(e){
      var r=e.getBoundingClientRect();
      if(r.top < window.innerHeight*1.1) e.classList.add('in');
    });
  }, 200);
});
