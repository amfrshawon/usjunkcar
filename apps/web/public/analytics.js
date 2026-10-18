// Site events for Google Tag Manager. Pushes named events to window.dataLayer; GTM decides where
// they go (GA4, Clarity). No personal data is sent: no ZIP codes, phone numbers or form values.
(() => {
  const dataLayer = (window.dataLayer = window.dataLayer || []);
  const clean = text => (text || '').replace(/\s+/g, ' ').trim().slice(0, 100);

  // Where on the page a control sits: header, footer, or the heading of its section.
  const locate = el => {
    if (el.closest('header')) return 'header';
    if (el.closest('footer')) return 'footer';
    const section = el.closest('section');
    const heading = section && section.querySelector('h1, h2');
    return heading ? clean(heading.textContent) : 'content';
  };

  const push = (event, el, extra) =>
    dataLayer.push({ event, cta_location: locate(el), cta_text: clean(el.textContent), ...extra });

  // Capture phase, so the events fire even when the Peddle script handles the click itself.
  document.addEventListener('click', e => {
    const link = e.target instanceof Element && e.target.closest('a');
    if (!link) return;
    const href = link.getAttribute('href') || '';
    if (link.hasAttribute('data-peddle-offer')) push('offer_open', link);
    else if (href.startsWith('tel:')) push('phone_click', link);
    else if (href.startsWith('mailto:')) push('email_click', link);
  }, true);

  document.addEventListener('submit', e => {
    const form = e.target;
    if (!(form instanceof HTMLFormElement) || !form.matches('.search-form')) return;
    const value = (form.querySelector('input')?.value || '').trim();
    push('zip_submit', form, { cta_text: 'ZIP search', zip_entered: /^\d{5}/.test(value) });
  }, true);

  // FAQ answers are <details> elements; record the question when one is opened.
  document.addEventListener('toggle', e => {
    const item = e.target;
    if (!(item instanceof HTMLDetailsElement) || !item.open) return;
    push('faq_open', item, { cta_text: clean(item.querySelector('summary')?.textContent) });
  }, true);
})();
