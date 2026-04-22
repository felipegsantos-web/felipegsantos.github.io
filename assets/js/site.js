/* site.js — Felipe G. Santos v2 */
(function(){
'use strict';

/* ── Cookie helpers ────────────────────────────────────────── */
function getCookie(n){var m=document.cookie.match(new RegExp('(?:^|;\\s*)'+n+'=([^;]*)'));return m?decodeURIComponent(m[1]):null}
function setCookie(n,v,d){var e=new Date(Date.now()+d*864e5).toUTCString();document.cookie=n+'='+encodeURIComponent(v)+';expires='+e+';path=/;SameSite=Lax'}

/* ── Detect lang ───────────────────────────────────────────── */
var currentLang=window.location.pathname.startsWith('/es')?'es':'en';

/* ── Lang toggle ───────────────────────────────────────────── */
document.querySelectorAll('[data-lang-btn]').forEach(function(btn){
  var lang=btn.dataset.langBtn;
  if(lang===currentLang){btn.classList.add('active');btn.setAttribute('aria-current','true')}
  btn.addEventListener('click',function(){setCookie('site_lang',lang,365)})
});

/* ── Theme ─────────────────────────────────────────────────── */
var html=document.documentElement;
var prefersDark=window.matchMedia('(prefers-color-scheme:dark)').matches;
var _theme='light';
try{_theme=localStorage.getItem('site-theme')||(prefersDark?'dark':'light')}catch(e){}
html.setAttribute('data-theme',_theme);

function updateThemeBtn(t){
  document.querySelectorAll('[data-theme-toggle]').forEach(function(btn){
    btn.setAttribute('aria-label','Switch to '+(t==='dark'?'light':'dark')+' mode');
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

/* ── Active nav ────────────────────────────────────────────── */
var path=window.location.pathname;
document.querySelectorAll('.site-nav__link,.mobile-nav__link,.footer-nav__link').forEach(function(a){
  var href=a.getAttribute('href');
  if(!href)return;
  if(path===href||(href.length>4&&path.startsWith(href)))a.classList.add('active')
});

/* ── Mobile nav ────────────────────────────────────────────── */
var mBtn=document.querySelector('.mobile-menu-btn');
var mNav=document.querySelector('.mobile-nav');
if(mBtn&&mNav){
  mBtn.addEventListener('click',function(){
    var open=mBtn.getAttribute('aria-expanded')==='true';
    mBtn.setAttribute('aria-expanded',String(!open));
    mNav.classList.toggle('open',!open);
    document.body.style.overflow=open?'':'hidden'
  });
  mNav.querySelectorAll('a').forEach(function(a){
    a.addEventListener('click',function(){mBtn.setAttribute('aria-expanded','false');mNav.classList.remove('open');document.body.style.overflow=''})
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
      btns.forEach(function(b){b.classList.remove('active')});
      btn.classList.add('active');
      var f=btn.dataset.filter;
      document.querySelectorAll('.pub-entry').forEach(function(el){
        if(f==='all'){el.hidden=false}
        else{el.hidden=!((el.dataset.pub||'').includes(f))}
      })
    })
  })
})();
// Media format filter
(function(){
  var btns=document.querySelectorAll('[data-media-filter]');
  if(!btns.length)return;
  btns.forEach(function(btn){
    btn.addEventListener('click',function(){
      btns.forEach(function(b){b.classList.remove('active')});
      btn.classList.add('active');
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

/* ── Analytics ─────────────────────────────────────────────── */
window.trackEvent=function(name,props){if(typeof window.plausible==='function')window.plausible(name,{props:props||{}})};
document.querySelectorAll('a[data-track]').forEach(function(a){
  a.addEventListener('click',function(){window.trackEvent(a.dataset.track,{url:a.dataset.trackLabel||a.href,lang:currentLang})})
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
      btns.forEach(function(b){b.classList.remove('active')});
      btn.classList.add('active');
      var v=btn.dataset.view;
      if(viewTheme)viewTheme.hidden=(v!=='theme');
      if(viewList)viewList.hidden=(v!=='list');
    });
  });
})();
