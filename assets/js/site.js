/* site.js — Felipe G. Santos v2 */
(function(){
'use strict';

/* ── Cookie helpers ────────────────────────────────────────── */
function getCookie(n){var m=document.cookie.match(new RegExp('(?:^|;\\s*)'+n+'=([^;]*)'));return m?decodeURIComponent(m[1]):null}
function setCookie(n,v,d){var e=new Date(Date.now()+d*864e5).toUTCString();document.cookie=n+'='+encodeURIComponent(v)+';expires='+e+';path=/;SameSite=Lax'}

/* ── Lang toggle: remember the choice for the root redirect ── */
/* The current language and the link to the equivalent page are rendered by the templates. */
document.querySelectorAll('[data-lang-btn]').forEach(function(btn){
  btn.addEventListener('click',function(){setCookie('site_lang',btn.dataset.langBtn,365)})
});

/* ── Theme ─────────────────────────────────────────────────── */
var html=document.documentElement;
var prefersDark=window.matchMedia('(prefers-color-scheme:dark)').matches;
var _theme='light';
try{_theme=localStorage.getItem('site-theme')||(prefersDark?'dark':'light')}catch(e){}
html.setAttribute('data-theme',_theme);

function updateThemeBtn(t){
  document.querySelectorAll('[data-theme-toggle]').forEach(function(btn){
    btn.setAttribute('aria-label',t==='dark'?btn.dataset.labelToLight:btn.dataset.labelToDark);
    btn.innerHTML=t==='dark'
      ?'<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>'
      :'<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>'
  })
}
updateThemeBtn(_theme);
document.querySelectorAll('[data-theme-toggle]').forEach(function(btn){
  btn.addEventListener('click',function(){
    _theme=_theme==='dark'?'light':'dark';
    html.setAttribute('data-theme',_theme);
    try{localStorage.setItem('site-theme',_theme)}catch(e){}
    updateThemeBtn(_theme)
  })
});

/* ── Sticky header ─────────────────────────────────────────── */
var hdr=document.querySelector('.site-header');
if(hdr){window.addEventListener('scroll',function(){hdr.classList.toggle('scrolled',window.scrollY>40)},{passive:true})}

/* ── Mobile nav ────────────────────────────────────────────── */
/* While the menu covers the page, main and footer are inert (no focus, no reading behind it).
   Escape closes it and returns focus to the button; so does growing past the mobile breakpoint. */
var mBtn=document.querySelector('.mobile-menu-btn');
var mNav=document.querySelector('.mobile-nav');
if(mBtn&&mNav){
  var behind=document.querySelectorAll('main,.site-footer');
  function setMenu(open,refocus){
    mBtn.setAttribute('aria-expanded',String(open));
    mBtn.setAttribute('aria-label',open?mBtn.dataset.labelClose:mBtn.dataset.labelOpen);
    mNav.classList.toggle('open',open);
    document.body.style.overflow=open?'hidden':'';
    behind.forEach(function(el){if(open)el.setAttribute('inert','');else el.removeAttribute('inert')});
    if(!open&&refocus)mBtn.focus()
  }
  mBtn.addEventListener('click',function(){setMenu(mBtn.getAttribute('aria-expanded')!=='true',false)});
  mNav.querySelectorAll('a').forEach(function(a){a.addEventListener('click',function(){setMenu(false,false)})});
  document.addEventListener('keydown',function(e){
    if(e.key==='Escape'&&mBtn.getAttribute('aria-expanded')==='true')setMenu(false,true)
  });
  window.matchMedia('(min-width:701px)').addEventListener('change',function(e){
    if(e.matches&&mBtn.getAttribute('aria-expanded')==='true')setMenu(false,false)
  })
}

/* ── Expandable summaries ──────────────────────────────────── */
document.querySelectorAll('.expand-toggle').forEach(function(btn){
  var id=btn.getAttribute('aria-controls');
  var tgt=id?document.getElementById(id):null;
  if(!tgt)return;
  btn.addEventListener('click',function(){
    var exp=btn.getAttribute('aria-expanded')==='true';
    btn.setAttribute('aria-expanded',String(!exp));
    tgt.classList.toggle('open',!exp)
  })
});

/* ── CV subnav active on scroll ────────────────────────────── */
var cvLinks=document.querySelectorAll('.cv-subnav__link');
if(cvLinks.length){
  var secs=Array.from(cvLinks).map(function(l){return document.getElementById(l.getAttribute('href').replace('#',''))}).filter(Boolean);
  new IntersectionObserver(function(entries){
    entries.forEach(function(e){
      if(e.isIntersecting){var id=e.target.id;cvLinks.forEach(function(l){l.classList.toggle('active',l.getAttribute('href')==='#'+id)})}
    })
  },{rootMargin:'-20% 0px -70% 0px'}).observe&&secs.forEach(function(s){new IntersectionObserver(function(entries){entries.forEach(function(e){if(e.isIntersecting){var id=e.target.id;cvLinks.forEach(function(l){l.classList.toggle('active',l.getAttribute('href')==='#'+id)})}})},{rootMargin:'-20% 0px -70% 0px'}).observe(s)})
}

/* ── Pub filter ────────────────────────────────────────────── */
function makeFilter(searchId,clearId,selector,keys){
  var inputs=keys.map(function(k){return{el:document.getElementById(k.id),attr:k.attr}}).filter(function(o){return o.el});
  var search=document.getElementById(searchId);
  var clear=document.getElementById(clearId);
  var items=document.querySelectorAll(selector);
  if(!items.length)return;
  function run(){
    var q=search?search.value.toLowerCase():'';
    items.forEach(function(el){
      var txt=el.textContent.toLowerCase();
      var show=(!q||txt.includes(q))&&inputs.every(function(o){var v=o.el.value;return!v||el.dataset[o.attr]===v||(el.dataset[o.attr]||'').includes(v)});
      el.style.display=show?'':'none'
    })
  }
  if(search)search.addEventListener('input',run);
  inputs.forEach(function(o){o.el.addEventListener('change',run)});
  if(clear)clear.addEventListener('click',function(){if(search)search.value='';inputs.forEach(function(o){o.el.value=''});run()})
}
makeFilter('pub-search','pub-clear','[data-pub]',[{id:'pub-filter-type',attr:'type'},{id:'pub-filter-year',attr:'year'}]);
makeFilter('media-search','media-clear','[data-media]',[{id:'media-filter-year',attr:'year'},{id:'media-filter-outlet',attr:'outlet'}]);

/* ── Button filter (type pills) ───────────────────────────── */
// Publication type filter
(function(){
  var btns=document.querySelectorAll('[data-filter]');
  if(!btns.length)return;
  btns.forEach(function(btn){
    btn.addEventListener('click',function(){
      btns.forEach(function(b){b.classList.remove('active');b.setAttribute('aria-pressed','false')});
      btn.classList.add('active');btn.setAttribute('aria-pressed','true');
      var f=btn.dataset.filter;
      var shown=0;
      document.querySelectorAll('.pub-entry').forEach(function(el){
        if(f==='all'){el.hidden=false}
        else{el.hidden=!((el.dataset.pub||'').includes(f))}
        if(!el.hidden)shown++
      });
      var live=document.getElementById('pub-count');
      if(live)live.textContent=shown+' '+(shown===1?live.dataset.one:live.dataset.other)
    })
  })
})();
// Media format filter
(function(){
  var btns=document.querySelectorAll('[data-media-filter]');
  if(!btns.length)return;
  btns.forEach(function(btn){
    btn.addEventListener('click',function(){
      btns.forEach(function(b){b.classList.remove('active');b.setAttribute('aria-pressed','false')});
      btn.classList.add('active');btn.setAttribute('aria-pressed','true');
      var f=btn.dataset.mediaFilter;
      document.querySelectorAll('.media-entry').forEach(function(el){
        if(f==='all'){el.hidden=false}
        else{el.hidden=!((el.dataset.media||'').toLowerCase().includes(f.toLowerCase()))}
      })
    })
  })
})();

/* ── Citation copy ─────────────────────────────────────────── */
document.querySelectorAll('[data-copy-citation]').forEach(function(btn){
  btn.addEventListener('click',function(){
    navigator.clipboard&&navigator.clipboard.writeText(btn.dataset.copyCitation).then(function(){var o=btn.textContent;btn.textContent='Copied!';setTimeout(function(){btn.textContent=o},1800)})
  })
});

})();

/* ── Publication view toggle (theme / flat list) ────────────── */
(function(){
  var btns=document.querySelectorAll('.view-btn');
  if(!btns.length)return;
  var viewTheme=document.getElementById('view-theme');
  var viewList=document.getElementById('view-list');
  btns.forEach(function(btn){
    btn.addEventListener('click',function(){
      btns.forEach(function(b){b.classList.remove('active');b.setAttribute('aria-pressed','false')});
      btn.classList.add('active');btn.setAttribute('aria-pressed','true');
      var v=btn.dataset.view;
      if(viewTheme)viewTheme.hidden=(v!=='theme');
      if(viewList)viewList.hidden=(v!=='list');
    });
  });
/* ── CV page (phones): the section menu closes after a link is used ── */
document.querySelectorAll('.cv-jump a').forEach(function(a){
  a.addEventListener('click',function(){var d=a.closest('details');if(d)d.removeAttribute('open')})
});

})();
