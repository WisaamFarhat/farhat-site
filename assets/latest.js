// Fills latest-issue details across the site from /data/site.json, so publishing a
// new IFIC only requires uploading the new page + updated site.json. Every element
// carries a sensible static fallback for no-JS and crawlers.
(function(){
  function $(s,root){return (root||document).querySelector(s);}
  function $$(s,root){return [...(root||document).querySelectorAll(s)];}
  fetch('/data/site.json',{cache:'no-cache'}).then(r=>r.json()).then(D=>{
    const issues=D.issues||[]; if(!issues.length) return;
    const L=issues[0];

    // feed the hero orbital scene on pages that ship an empty static feed
    if(window.__setOrbitFilings && (!window.ORBIT_FILINGS || !window.ORBIT_FILINGS.length) && L.orbit){
      window.__setOrbitFilings(L.orbit);
    }

    // — generic latest slots —
    $$('[data-l-no]').forEach(e=>e.textContent=L.no);
    $$('[data-l-cta]').forEach(a=>{a.textContent='Read the latest, IFIC '+L.no+' \u2192'; a.href='/ific/'+L.no+'/';});
    $$('[data-l-open]').forEach(a=>{a.textContent='Open IFIC '+L.no+' \u2192'; a.href='/ific/'+L.no+'/';});
    $$('[data-l-heading]').forEach(e=>e.innerHTML='IFIC '+L.no+'<span style="display:inline-block;width:1px;height:.7em;background:var(--line);margin:0 18px;vertical-align:baseline"></span>'+L.pub_h);
    $$('[data-l-summary]').forEach(e=>e.textContent=L.summary);
    $$('[data-l-foot]').forEach(a=>{a.textContent='IFIC '+L.no+' (latest)'; a.href='/ific/'+L.no+'/';});

    // — subscribe preview card —
    $$('[data-l-pv-issue]').forEach(e=>e.textContent='IFIC '+L.no);
    $$('[data-l-pv-stats]').forEach(e=>e.textContent=L.filings+' coordination filings, '+L.gso+' GSO / '+L.ngso+' NGSO');
    $$('[data-l-pv-lead]').forEach(e=>e.textContent='Lead filing: '+L.lead_line);
    $$('[data-l-pv-fleet]').forEach(e=>{ if(L.fleet_line){e.textContent=L.fleet_line;} else {e.style.display='none';} });
    $$('[data-l-pv-deadline]').forEach(e=>e.innerHTML='Comment deadline: <span style="color:var(--sand-lt)">'+L.deadline_h+'</span>');
    $$('[data-l-pv-link]').forEach(a=>a.href='/ific/'+L.no+'/');

    // — schedule page statuses (live, computed with the viewer's date) —
    const today=new Date(); today.setHours(0,0,0,0);
    const decoded=new Set(issues.map(i=>i.no));
    let nextRow=null;
    $$('tr[data-ific]').forEach(tr=>{
      const n=tr.getAttribute('data-ific');
      const pd=new Date(tr.getAttribute('data-pub'));
      const cell=$('[data-status]',tr); if(!cell) return;
      if(decoded.has(n)){
        cell.innerHTML='<a href="/ific/'+n+'/" style="color:var(--sand);font-weight:500">Read the digest \u2192</a>';
      } else if(pd<=today){
        cell.innerHTML='<span style="color:var(--muted)">Published, digest pending</span>';
      } else {
        cell.innerHTML='<span class="mono" style="font-size:.78rem;letter-spacing:.08em;color:var(--muted)">UPCOMING</span>';
        if(!nextRow) nextRow=tr;
      }
      tr.style.background='';
    });
    if(nextRow) nextRow.style.background='var(--paper-2)';

    // — IFIC pages: live deadline chip + prev/next from the issues list —
    $$('[data-chip][data-deadline]').forEach(chip=>{
      const dl=new Date(chip.getAttribute('data-deadline')); dl.setHours(0,0,0,0);
      const days=Math.round((dl-today)/86400000);
      const st=$('[data-chip-status]',chip);
      chip.classList.remove('urgent','past');
      if(days<0){ chip.classList.add('past'); if(st) st.textContent='Closed'; }
      else if(days===0){ chip.classList.add('urgent'); if(st) st.textContent='Closes today'; }
      else { if(days<=30) chip.classList.add('urgent'); if(st) st.textContent=days+' days left'; }
    });
    const here=$('[data-this-ific]');
    if(here){
      const n=here.getAttribute('data-this-ific');
      const order=issues.map(i=>i.no).sort();
      const i=order.indexOf(n);
      const prev=i>0?order[i-1]:null, next=(i>=0&&i<order.length-1)?order[i+1]:null;
      const pa=$('[data-nav-prev]'), na=$('[data-nav-next]');
      if(pa&&prev){pa.textContent='\u2190 IFIC '+prev; pa.href='/ific/'+prev+'/'; pa.removeAttribute('hidden');}
      if(na&&next){na.textContent='IFIC '+next+' \u2192'; na.href='/ific/'+next+'/'; na.removeAttribute('hidden');}
    }
  }).catch(()=>{ /* static fallbacks remain */ });
})();
