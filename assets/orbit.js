// Orbital arc signature. Plots real GSO filings along the geostationary belt.
// Data injected per-page as window.ORBIT_FILINGS = [{name, pos, type}]
(function(){
  const canvas = document.getElementById('orbit-canvas');
  if(!canvas) return;
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const ctx = canvas.getContext('2d');
  let W,H,DPR;
  function resize(){
    DPR = Math.min(window.devicePixelRatio||1, 2);
    W = canvas.clientWidth; H = canvas.clientHeight;
    canvas.width = W*DPR; canvas.height = H*DPR;
    ctx.setTransform(DPR,0,0,DPR,0,0);
  }
  const filings = (window.ORBIT_FILINGS||[]).filter(f=>f.type==='GSO' && typeof f.deg==='number');
  const stars = Array.from({length:70},()=>({x:Math.random(),y:Math.random(),r:Math.random()*1.2+.2,tw:Math.random()*Math.PI*2}));
  let t=0, raf;
  function draw(){
    t += reduce?0:0.006;
    ctx.clearRect(0,0,W,H);
    // ambient stars
    stars.forEach(s=>{
      const a = .3 + .5*Math.abs(Math.sin(s.tw + t*2));
      ctx.fillStyle = `rgba(196,168,130,${a*0.5})`;
      ctx.beginPath(); ctx.arc(s.x*W, s.y*H, s.r, 0, 7); ctx.fill();
    });
    // Earth centre (lower-right, partially off) with the GSO arc sweeping across
    const cx = W*0.5, cy = H*1.35, R = H*1.15;
    // the arc
    ctx.lineWidth = 1.2;
    ctx.strokeStyle = 'rgba(196,168,130,0.28)';
    ctx.beginPath(); ctx.arc(cx, cy, R, Math.PI*1.18, Math.PI*1.82); ctx.stroke();
    // faint second arc
    ctx.strokeStyle='rgba(196,168,130,0.10)';
    ctx.beginPath(); ctx.arc(cx, cy, R*0.86, Math.PI*1.2, Math.PI*1.8); ctx.stroke();
    // plot filings along the arc by longitude (-180..180 -> arc span)
    filings.forEach((f,i)=>{
      const frac = (f.deg + 180)/360;            // 0..1
      const ang = Math.PI*1.18 + frac*(Math.PI*0.64);
      const px = cx + R*Math.cos(ang), py = cy + R*Math.sin(ang);
      const pulse = 1 + 0.4*Math.sin(t*3 + i);
      // glow
      const g = ctx.createRadialGradient(px,py,0,px,py,10*pulse);
      g.addColorStop(0,'rgba(230,200,140,0.9)'); g.addColorStop(1,'rgba(230,200,140,0)');
      ctx.fillStyle=g; ctx.beginPath(); ctx.arc(px,py,10*pulse,0,7); ctx.fill();
      // core dot
      ctx.fillStyle = f.type==='GSO' ? '#E8DCC4' : '#C08829';
      ctx.beginPath(); ctx.arc(px,py,2.4,0,7); ctx.fill();
      // tick to arc
      ctx.strokeStyle='rgba(232,220,196,0.25)'; ctx.lineWidth=.8;
      ctx.beginPath(); ctx.moveTo(px,py);
      ctx.lineTo(cx + (R-14)*Math.cos(ang), cy + (R-14)*Math.sin(ang)); ctx.stroke();
    });
    if(!reduce) raf = requestAnimationFrame(draw);
  }
  function start(){ resize(); draw(); }
  window.addEventListener('resize', ()=>{ resize(); if(reduce){ctx.clearRect(0,0,W,H);draw();} });
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
