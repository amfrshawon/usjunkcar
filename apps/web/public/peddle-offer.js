// Peddle Publisher Embed: every "Online Quote" / "Get Cash Offer" control and the ZIP search
// open the Peddle offer modal. The bootstrap snippet and publisher ID live in index.html <head>.
(() => {
  // Always call through window: the bootstrap stub is replaced by the real API once Peddle's script loads.
  const embed = (operation, options) => window.PeddlePublisherEmbed(operation, options);
  if (typeof window.PeddlePublisherEmbed !== 'function') return; // no publisher ID: links keep their fallback

  embed('boot');

  document.querySelectorAll('[data-peddle-offer]').forEach(link => {
    link.addEventListener('click', event => {
      event.preventDefault();
      embed('open');
    });
  });

  // The hero search asks for "City or ZIP code"; a US ZIP prefills the offer, anything else just opens it.
  const form = document.querySelector('.search-form');
  if (form) {
    form.addEventListener('submit', event => {
      event.preventDefault();
      const zip = (form.querySelector('input')?.value || '').trim().match(/^\d{5}/);
      if (zip) embed('hydrate', { zipcode: zip[0] });
      embed('open');
    }, true);
  }
})();
