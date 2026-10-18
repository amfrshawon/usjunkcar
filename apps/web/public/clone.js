'use strict';
const header = document.querySelector('.header');
const toggle = document.querySelector('.header__hamburger');
const nav = document.querySelector('.header__nav-inner');
const desktop = window.matchMedia('(min-width: 992px)');
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
nav.id = 'site-navigation';
toggle.setAttribute('aria-controls', nav.id);
function setMenu(open, restoreFocus = false) {
  header.classList.toggle('menu-active', open);
  toggle.classList.toggle('active', open);
  nav.classList.toggle('active', open);
  toggle.setAttribute('aria-expanded', String(open));
  nav.inert = !desktop.matches && !open;
  document.body.style.overflow = open ? 'hidden' : '';
  if (restoreFocus) toggle.focus();
}
setMenu(false);
toggle.addEventListener('click', () => setMenu(!nav.classList.contains('active')));
desktop.addEventListener('change', () => setMenu(false));
document.addEventListener('keydown', event => {
  if (!nav.classList.contains('active')) return;
  if (event.key === 'Escape') { event.preventDefault(); setMenu(false, true); }
  if (event.key === 'Tab') {
    const controls = [...header.querySelectorAll('a,button')].filter(el => el.getClientRects().length && !el.closest('[inert]'));
    const first = controls[0], last = controls.at(-1);
    if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
    else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
  }
});
nav.addEventListener('click', event => { if (event.target.closest('a')) setMenu(false); });
const accordionButtons = [...nav.querySelectorAll('.faq-accordion__header')];
function setAccordion(button, open) {
  button.classList.toggle('active', open);
  button.parentElement.classList.toggle('active', open);
  button.setAttribute('aria-expanded', String(open));
  button.nextElementSibling.hidden = !open;
  button.nextElementSibling.style.maxHeight = open ? `${button.nextElementSibling.scrollHeight}px` : '';
}
accordionButtons.forEach((button, i) => {
  button.nextElementSibling.id = `submenu-${i}`;
  button.setAttribute('aria-controls', `submenu-${i}`);
  setAccordion(button, false);
  button.addEventListener('click', () => {
    const open = button.getAttribute('aria-expanded') !== 'true';
    accordionButtons.forEach(other => setAccordion(other, other === button && open));
  });
});
const topButton = document.querySelector('.top-button');
function updateScroll() {
  header.classList.toggle('scrolling', window.scrollY > 20);
  topButton.hidden = window.scrollY < 400;
}
window.addEventListener('scroll', updateScroll, {passive: true});
updateScroll();
topButton.addEventListener('click', event => {
  event.preventDefault();
  window.scrollTo({top: 0, behavior: reducedMotion.matches ? 'instant' : 'smooth'});
});
// Homepage-only widgets below are skipped on inner pages.
const input = document.querySelector('.search-form__input');
if (input) {
  input.required = true;
  input.setAttribute('aria-label', 'ZIP code for an instant offer');
  input.form.addEventListener('submit', event => {
    input.value = input.value.trim();
    if (!input.value) { event.preventDefault(); input.reportValidity(); }
  });
}
// Native scrolling keeps every brand accessible by touch, keyboard and pagination.
const brands = document.querySelector('.brands-slider');
if (brands) {
  const brandTrack = brands.querySelector('.swiper-wrapper');
  const brandPagination = brands.querySelector('.swiper-pagination');
  brandTrack.tabIndex = 0;
  brandTrack.setAttribute('role', 'region');
  brandTrack.setAttribute('aria-label', 'Popular vehicle brands');
  let brandDots = [];
  function updateBrandDots() {
    const page = Math.round(brandTrack.scrollLeft / brandTrack.clientWidth);
    brandDots.forEach((dot, i) => {
      dot.classList.toggle('swiper-pagination-bullet-active', i === page);
      dot.setAttribute('aria-current', String(i === page));
    });
  }
  function layoutBrands() {
    const pages = Math.max(1, Math.ceil(brandTrack.scrollWidth / brandTrack.clientWidth));
    brandPagination.replaceChildren();
    brandDots = Array.from({length: pages}, (_, i) => {
      const dot = document.createElement('button');
      dot.type = 'button'; dot.className = 'swiper-pagination-bullet';
      dot.setAttribute('aria-label', `Show brand page ${i + 1}`);
      dot.addEventListener('click', () => brandTrack.scrollTo({left: i * brandTrack.clientWidth, behavior: reducedMotion.matches ? 'instant' : 'smooth'}));
      brandPagination.append(dot);
      return dot;
    });
    updateBrandDots();
  }
  new ResizeObserver(layoutBrands).observe(brandTrack);
  brandTrack.addEventListener('scroll', updateBrandDots, {passive: true});
  brandTrack.addEventListener('keydown', event => {
    if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
      event.preventDefault();
      brandTrack.scrollBy({left: (event.key === 'ArrowRight' ? 1 : -1) * brandTrack.clientWidth, behavior: reducedMotion.matches ? 'instant' : 'smooth'});
    }
  });
  // Auto-slide one logo every 1.6 s while the slider is on screen, looping back at the end. It pauses
  // while the visitor hovers, touches or focuses it (and for 4 s after), and never runs with reduced motion.
  let brandVisible = false, brandHeld = false, brandResumeAt = 0;
  new IntersectionObserver(([entry]) => { brandVisible = entry.isIntersecting; }, {threshold: 0.3}).observe(brands);
  const holdBrands = () => { brandHeld = true; };
  const releaseBrands = () => { brandHeld = false; brandResumeAt = Date.now() + 4000; };
  brands.addEventListener('pointerenter', holdBrands);
  brands.addEventListener('pointerleave', releaseBrands);
  brandTrack.addEventListener('touchstart', holdBrands, {passive: true});
  brandTrack.addEventListener('touchend', releaseBrands, {passive: true});
  brands.addEventListener('focusin', holdBrands);
  brands.addEventListener('focusout', releaseBrands);
  setInterval(() => {
    if (reducedMotion.matches || !brandVisible || brandHeld || document.hidden || Date.now() < brandResumeAt) return;
    const item = brandTrack.querySelector('.brands-slider__item');
    const step = item ? item.getBoundingClientRect().width + 8 : brandTrack.clientWidth / 4;
    const atEnd = brandTrack.scrollLeft + brandTrack.clientWidth >= brandTrack.scrollWidth - 4;
    brandTrack.scrollTo({left: atEnd ? 0 : brandTrack.scrollLeft + step, behavior: 'smooth'});
  }, 1600);
}
const stateName = link => (link.getAttribute('data-state') || link.querySelector('[data-state]')?.getAttribute('data-state') ||
  new URL(link.href.baseVal ?? link.href, location.href).pathname.slice(1).replaceAll('-', ' ')).replace(/\b\w/g, c => c.toUpperCase());
function labelMapLinks() {
  document.querySelectorAll('.map svg a').forEach(link => {
    if (!link.hasAttribute('aria-label')) link.setAttribute('aria-label', `Cash for junk cars in ${stateName(link)}`);
    link.querySelectorAll('title').forEach(t => t.remove()); // the browser's own tooltip waits ~1 s; ours is instant
  });
}
labelMapLinks();
// Map label: appears instantly beside the pointer, follows it smoothly, flips at the screen edges, and also
// shows for keyboard focus. Touch devices skip it (a tap opens the offer straight away).
const mapBox = document.querySelector('.map');
if (mapBox && matchMedia('(hover: hover)').matches) {
  const tip = document.createElement('div');
  tip.className = 'map-tip';
  tip.setAttribute('aria-hidden', 'true');
  tip.innerHTML = '<span class="map-tip__dot"></span><span><strong class="map-tip__name"></strong><span class="map-tip__cta">Get your instant offer →</span></span>';
  document.body.append(tip);
  const nameEl = tip.querySelector('.map-tip__name');
  let current = null, x = 0, y = 0, frame = 0;
  const place = () => {
    frame = 0;
    const w = tip.offsetWidth, h = tip.offsetHeight, gap = 18;
    let left = x + gap, top = y - h - gap;
    if (left + w > innerWidth - 8) left = x - w - gap;
    if (top < 8) top = y + gap;
    tip.style.transform = `translate3d(${Math.round(left)}px, ${Math.round(top)}px, 0)`;
  };
  const show = link => {
    if (current !== link) { current = link; nameEl.textContent = stateName(link); }
    tip.classList.add('is-on');
    if (!frame) frame = requestAnimationFrame(place);
  };
  const hide = () => { current = null; tip.classList.remove('is-on'); };
  mapBox.addEventListener('pointermove', event => {
    const link = event.target instanceof Element && event.target.closest('svg a');
    if (!link) return hide();
    x = event.clientX; y = event.clientY; show(link);
  });
  mapBox.addEventListener('pointerleave', hide);
  mapBox.addEventListener('focusin', event => {
    const link = event.target instanceof Element && event.target.closest('svg a');
    if (!link) return;
    const r = link.getBoundingClientRect();
    x = r.left + r.width / 2; y = r.top + r.height / 2; show(link);
  });
  mapBox.addEventListener('focusout', hide);
  addEventListener('scroll', hide, {passive: true});
}
// The homepage map is ~100 KB of SVG, so it is fetched when it nears the viewport instead of being
// part of the page. Its box has a fixed height, so nothing moves when it arrives.
const mapSlot = document.querySelector('[data-map-src]');
if (mapSlot) {
  const loadMap = () => fetch(mapSlot.dataset.mapSrc)
    .then(res => (res.ok ? res.text() : Promise.reject(new Error(`map ${res.status}`))))
    .then(svg => { mapSlot.innerHTML = svg; labelMapLinks(); })
    .catch(() => {});
  if ('IntersectionObserver' in window) {
    const near = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) { near.disconnect(); loadMap(); }
    }, {rootMargin: '150% 0px'});
    near.observe(mapSlot);
  } else loadMap();
}

// Blog 6-Topic Section filter and live keyword search.
const blogTopicSections = [...document.querySelectorAll('[data-blog-topic-section]')];
if (blogTopicSections.length) {
  let activeCategory = 'all';
  const searchInput = document.getElementById('blog-search-input');
  const filterButtons = [...document.querySelectorAll('[data-blog-filter]')];
  const countLabel = document.getElementById('blog-results-count');
  const emptyState = document.getElementById('blog-empty-state');
  const allCards = [...document.querySelectorAll('[data-blog-card]')];

  function applyBlogFilters() {
    const query = (searchInput?.value || '').trim().toLowerCase();
    let visibleCount = 0;
    let visibleTopics = 0;

    blogTopicSections.forEach(section => {
      const sectionCat = section.getAttribute('data-blog-topic-section');
      const cards = [...section.querySelectorAll('[data-blog-card]')];
      let sectionVisibleCards = 0;

      cards.forEach(card => {
        const text = ((card.textContent || '') + ' ' + (card.getAttribute('data-keywords') || '')).toLowerCase();
        const matchCat = activeCategory === 'all' || sectionCat === activeCategory;
        const matchQuery = !query || text.includes(query);
        const show = matchCat && matchQuery;
        card.hidden = !show;
        if (show) {
          visibleCount++;
          sectionVisibleCards++;
        }
      });

      section.hidden = sectionVisibleCards === 0;
      if (sectionVisibleCards > 0) visibleTopics++;
    });

    if (countLabel) {
      countLabel.textContent =
        visibleCount === allCards.length
          ? `Showing all ${allCards.length} guides across ${blogTopicSections.length} topics`
          : `Showing ${visibleCount} of ${allCards.length} guides (${visibleTopics} ${visibleTopics === 1 ? 'topic' : 'topics'})`;
    }
    if (emptyState) emptyState.hidden = visibleCount > 0;
  }

  filterButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      activeCategory = btn.getAttribute('data-blog-filter') || 'all';
      filterButtons.forEach(b => {
        const isCurrent = b === btn;
        b.classList.toggle('is-active', isCurrent);
        b.setAttribute('aria-pressed', String(isCurrent));
      });
      applyBlogFilters();
    });
  });

  searchInput?.addEventListener('input', applyBlogFilters);
}
