/* ============================================================
   SITE JS — Language routing, theme, nav, filters, etc.
   ============================================================ */

(function () {
  'use strict';

  /* ---- Cookie helpers ---- */
  function getCookie(name) {
    const m = document.cookie.match(new RegExp('(?:^|;\\s*)' + name + '=([^;]*)'));
    return m ? decodeURIComponent(m[1]) : null;
  }
  function setCookie(name, value, days) {
    const exp = new Date(Date.now() + days * 864e5).toUTCString();
    document.cookie = name + '=' + encodeURIComponent(value) + '; expires=' + exp + '; path=/; SameSite=Lax';
  }

  /* ---- Language detection (only at /) ---- */
  if (window.__LANG_ROUTER__) {
    const stored = getCookie('site_lang');
    if (!stored) {
      const browser = (navigator.language || navigator.userLanguage || 'en').split('-')[0].toLowerCase();
      const dest = browser === 'es' ? '/es/' : '/en/';
      window.location.replace(dest);
    } else {
      window.location.replace(stored === 'es' ? '/es/' : '/en/');
    }
  }

  /* ---- Detect current language from URL ---- */
  const currentLang = window.location.pathname.startsWith('/es') ? 'es' : 'en';

  /* ---- Language toggle buttons ---- */
  document.querySelectorAll('[data-lang-btn]').forEach(function (btn) {
    const lang = btn.dataset.langBtn;
    if (lang === currentLang) {
      btn.classList.add('active');
      btn.setAttribute('aria-current', 'true');
    }
    btn.addEventListener('click', function () {
      setCookie('site_lang', lang, 365);
      // Navigation handled by href
    });
  });

  /* ---- Theme toggle ---- */
  const html = document.documentElement;
  function getStoredTheme() {
    try { return sessionStorage.getItem('theme'); } catch { return null; }
  }
  function setStoredTheme(t) {
    try { sessionStorage.setItem('theme', t); } catch {}
  }
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  let currentTheme = getStoredTheme() || (prefersDark ? 'dark' : 'light');
  html.setAttribute('data-theme', currentTheme);

  function updateThemeToggle(theme) {
    document.querySelectorAll('[data-theme-toggle]').forEach(function (btn) {
      btn.setAttribute('aria-label', 'Switch to ' + (theme === 'dark' ? 'light' : 'dark') + ' mode');
      btn.innerHTML = theme === 'dark'
        ? '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>'
        : '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
    });
  }

  updateThemeToggle(currentTheme);

  document.querySelectorAll('[data-theme-toggle]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      currentTheme = currentTheme === 'dark' ? 'light' : 'dark';
      html.setAttribute('data-theme', currentTheme);
      setStoredTheme(currentTheme);
      updateThemeToggle(currentTheme);
    });
  });

  /* ---- Sticky header scroll effect ---- */
  const header = document.querySelector('.site-header');
  if (header) {
    let lastScroll = 0;
    window.addEventListener('scroll', function () {
      const y = window.scrollY;
      if (y > 40) {
        header.classList.add('scrolled');
      } else {
        header.classList.remove('scrolled');
      }
      lastScroll = y;
    }, { passive: true });
  }

  /* ---- Active nav link ---- */
  const path = window.location.pathname;
  document.querySelectorAll('.site-nav__link, .mobile-nav__link, .footer-nav__link').forEach(function (link) {
    const href = link.getAttribute('href');
    if (href && path === href) {
      link.classList.add('active');
    } else if (href && href.length > 4 && path.startsWith(href)) {
      link.classList.add('active');
    }
  });

  /* ---- Mobile nav ---- */
  const mobileBtn = document.querySelector('.mobile-menu-btn');
  const mobileNav = document.querySelector('.mobile-nav');
  if (mobileBtn && mobileNav) {
    mobileBtn.addEventListener('click', function () {
      const open = mobileBtn.getAttribute('aria-expanded') === 'true';
      mobileBtn.setAttribute('aria-expanded', String(!open));
      mobileNav.classList.toggle('open', !open);
      document.body.style.overflow = open ? '' : 'hidden';
    });

    // Close on link click
    mobileNav.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () {
        mobileBtn.setAttribute('aria-expanded', 'false');
        mobileNav.classList.remove('open');
        document.body.style.overflow = '';
      });
    });
  }

  /* ---- Expandable summaries ---- */
  document.querySelectorAll('.expand-toggle').forEach(function (btn) {
    const targetId = btn.getAttribute('aria-controls');
    const target = targetId ? document.getElementById(targetId) : null;
    if (!target) return;
    btn.addEventListener('click', function () {
      const expanded = btn.getAttribute('aria-expanded') === 'true';
      btn.setAttribute('aria-expanded', String(!expanded));
      target.classList.toggle('open', !expanded);
    });
  });

  /* ---- CV subnav active on scroll ---- */
  const cvLinks = document.querySelectorAll('.cv-subnav__link');
  if (cvLinks.length) {
    const sections = Array.from(cvLinks).map(function (link) {
      const id = link.getAttribute('href').replace('#', '');
      return document.getElementById(id);
    }).filter(Boolean);

    const observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          const id = entry.target.id;
          cvLinks.forEach(function (link) {
            link.classList.toggle('active', link.getAttribute('href') === '#' + id);
          });
        }
      });
    }, { rootMargin: '-20% 0px -70% 0px' });

    sections.forEach(function (s) { observer.observe(s); });
  }

  /* ---- Publications filter ---- */
  const pubSearch = document.getElementById('pub-search');
  const pubFilterType = document.getElementById('pub-filter-type');
  const pubFilterYear = document.getElementById('pub-filter-year');
  const pubFilterTopic = document.getElementById('pub-filter-topic');
  const pubClear = document.getElementById('pub-clear');
  const pubEntries = document.querySelectorAll('[data-pub]');

  function filterPubs() {
    const q = (pubSearch ? pubSearch.value : '').toLowerCase();
    const type = pubFilterType ? pubFilterType.value : '';
    const year = pubFilterYear ? pubFilterYear.value : '';
    const topic = pubFilterTopic ? pubFilterTopic.value : '';

    pubEntries.forEach(function (el) {
      const text = el.textContent.toLowerCase();
      const elType = el.dataset.type || '';
      const elYear = el.dataset.year || '';
      const elTopics = el.dataset.topics || '';

      const matchQ = !q || text.includes(q);
      const matchType = !type || elType === type;
      const matchYear = !year || elYear === year;
      const matchTopic = !topic || elTopics.includes(topic);

      el.style.display = (matchQ && matchType && matchYear && matchTopic) ? '' : 'none';
    });
  }

  if (pubSearch) pubSearch.addEventListener('input', filterPubs);
  if (pubFilterType) pubFilterType.addEventListener('change', filterPubs);
  if (pubFilterYear) pubFilterYear.addEventListener('change', filterPubs);
  if (pubFilterTopic) pubFilterTopic.addEventListener('change', filterPubs);
  if (pubClear) {
    pubClear.addEventListener('click', function () {
      if (pubSearch) pubSearch.value = '';
      if (pubFilterType) pubFilterType.value = '';
      if (pubFilterYear) pubFilterYear.value = '';
      if (pubFilterTopic) pubFilterTopic.value = '';
      filterPubs();
    });
  }

  /* ---- Media filter ---- */
  const mediaSearch = document.getElementById('media-search');
  const mediaFilterYear = document.getElementById('media-filter-year');
  const mediaFilterOutlet = document.getElementById('media-filter-outlet');
  const mediaFilterTopic = document.getElementById('media-filter-topic');
  const mediaClear = document.getElementById('media-clear');
  const mediaItems = document.querySelectorAll('[data-media]');

  function filterMedia() {
    const q = (mediaSearch ? mediaSearch.value : '').toLowerCase();
    const year = mediaFilterYear ? mediaFilterYear.value : '';
    const outlet = mediaFilterOutlet ? mediaFilterOutlet.value : '';
    const topic = mediaFilterTopic ? mediaFilterTopic.value : '';

    mediaItems.forEach(function (el) {
      const text = el.textContent.toLowerCase();
      const elYear = el.dataset.year || '';
      const elOutlet = el.dataset.outlet || '';
      const elTopics = el.dataset.topics || '';

      const matchQ = !q || text.includes(q);
      const matchYear = !year || elYear === year;
      const matchOutlet = !outlet || elOutlet === outlet;
      const matchTopic = !topic || elTopics.includes(topic);

      el.style.display = (matchQ && matchYear && matchOutlet && matchTopic) ? '' : 'none';
    });
  }

  if (mediaSearch) mediaSearch.addEventListener('input', filterMedia);
  if (mediaFilterYear) mediaFilterYear.addEventListener('change', filterMedia);
  if (mediaFilterOutlet) mediaFilterOutlet.addEventListener('change', filterMedia);
  if (mediaFilterTopic) mediaFilterTopic.addEventListener('change', filterMedia);
  if (mediaClear) {
    mediaClear.addEventListener('click', function () {
      if (mediaSearch) mediaSearch.value = '';
      if (mediaFilterYear) mediaFilterYear.value = '';
      if (mediaFilterOutlet) mediaFilterOutlet.value = '';
      if (mediaFilterTopic) mediaFilterTopic.value = '';
      filterMedia();
    });
  }

  /* ---- Citation copy ---- */
  document.querySelectorAll('[data-copy-citation]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const text = btn.dataset.copyCitation;
      if (!text) return;
      navigator.clipboard.writeText(text).then(function () {
        const original = btn.textContent;
        btn.textContent = 'Copied!';
        setTimeout(function () { btn.textContent = original; }, 1800);
      });
    });
  });

  /* ---- Privacy analytics stub (Plausible-compatible) ---- */
  // Plausible is loaded via script tag in head; this tracks custom events
  window.trackEvent = function (name, props) {
    if (typeof window.plausible === 'function') {
      window.plausible(name, { props: props || {} });
    }
  };

  // Track outbound links
  document.querySelectorAll('a[data-track]').forEach(function (a) {
    a.addEventListener('click', function () {
      const category = a.dataset.track;
      const label = a.dataset.trackLabel || a.href;
      window.trackEvent(category, { url: label, lang: currentLang });
    });
  });

})();
