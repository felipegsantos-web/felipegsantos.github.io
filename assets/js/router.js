/* Language router — runs only on / (root) */
(function () {
  var stored = null;
  try {
    var m = document.cookie.match(/(?:^|;\s*)site_lang=([^;]*)/);
    stored = m ? decodeURIComponent(m[1]) : null;
  } catch (e) {}
  if (stored === 'es') { window.location.replace('/es/'); return; }
  if (stored === 'en') { window.location.replace('/en/'); return; }
  var browser = (navigator.language || navigator.userLanguage || 'en').split('-')[0].toLowerCase();
  window.location.replace(browser === 'es' ? '/es/' : '/en/');
})();
