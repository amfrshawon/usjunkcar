// Peddle Publisher Embed: every "Online Quote" / "Get Cash Offer" control and the ZIP search open the
// Peddle offer modal. The bootstrap stub and window.loadPeddleEmbed() are inlined in <head>; the embed
// script itself (and the captcha resources it pulls) is fetched only when a visitor first presses an
// offer control. If it cannot load, the controls fall back to their tel: link.
(() => {
  // Always call through window: the bootstrap stub is replaced by the real API once Peddle's script loads.
  const embed = (operation, options) => window.PeddlePublisherEmbed(operation, options);
  if (typeof window.PeddlePublisherEmbed !== 'function' || typeof window.loadPeddleEmbed !== 'function') return; // links keep their fallback

  const TIMEOUT_MS = 10000;
  const FALLBACK_TEL = 'tel:+18445120697';
  let state = 'idle'; // idle → loading → ready | failed
  let loading = null;
  let pending = null; // the control waiting for the first open

  const load = () => {
    if (!loading) {
      state = 'loading';
      embed('boot'); // queued in the stub, processed when the script arrives
      loading = new Promise((resolve, reject) => {
        setTimeout(() => reject(new Error('Peddle embed timed out')), TIMEOUT_MS);
        window.loadPeddleEmbed().then(resolve, reject);
      }).then(() => { state = 'ready'; }, () => { state = 'failed'; });
    }
    return loading;
  };

  // Resolves once Peddle's offer iframe has loaded (or after 3 s), so the loading state covers the gap.
  const frameShown = () => new Promise(resolve => {
    let timer;
    const observer = new MutationObserver(() => check());
    const done = () => { observer.disconnect(); clearTimeout(timer); resolve(); };
    const check = () => {
      const frame = [...document.querySelectorAll('iframe')].find(f => /peddle/i.test(f.src));
      if (frame) { observer.disconnect(); frame.addEventListener('load', done, { once: true }); }
    };
    timer = setTimeout(done, 3000);
    observer.observe(document.body, { childList: true, subtree: true });
    check();
  });

  const busy = (el, on) => {
    el.classList.toggle('is-loading', on);
    if (on) el.setAttribute('aria-busy', 'true'); else el.removeAttribute('aria-busy');
  };

  // Opens the offer; returns false when the caller should use the phone fallback instead.
  const open = (el, zip) => {
    if (state === 'failed') return false;
    if (state === 'idle') load();
    if (zip) embed('hydrate', { zipcode: zip });
    if (state === 'ready') { embed('open'); return true; }
    if (pending) return true; // already opening
    pending = el;
    busy(el, true);
    loading.then(() => {
      pending = null;
      if (state === 'ready') {
        embed('open');
        frameShown().then(() => busy(el, false));
      } else {
        busy(el, false);
        window.location.href = el.getAttribute('href')?.startsWith('tel:') ? el.getAttribute('href') : FALLBACK_TEL;
      }
    });
    return true;
  };

  // Start fetching on press, so the script is usually on its way before the click event fires.
  document.addEventListener('pointerdown', event => {
    if (state === 'idle' && event.target instanceof Element && event.target.closest('[data-peddle-offer]')) load();
  }, { capture: true, passive: true });

  // Delegated, so controls added later (the lazily loaded homepage map) open the offer too.
  document.addEventListener('click', event => {
    const link = event.target instanceof Element && event.target.closest('[data-peddle-offer]');
    if (link && open(link)) event.preventDefault();
  });

  // The hero search asks for "City or ZIP code"; a US ZIP prefills the offer, anything else just opens it.
  const form = document.querySelector('.search-form');
  if (form) {
    form.addEventListener('submit', event => {
      event.preventDefault();
      const zip = (form.querySelector('input')?.value || '').trim().match(/^\d{5}/);
      if (!open(form.querySelector('button') || form, zip && zip[0])) window.location.href = FALLBACK_TEL;
    }, true);
  }
})();
