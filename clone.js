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
// The reference opens the selected question on its FAQ page in a new tab.
document.querySelectorAll('.js-link-faq a').forEach(link => {
  link.href = `https://www.usjunkcars.com/faqs?name=${encodeURIComponent(link.textContent.trim())}`;
  link.target = '_blank'; link.rel = 'noopener';
});
const input = document.querySelector('.search-form__input');
input.required = true;
input.setAttribute('aria-label', 'Search by city or ZIP code');
input.form.addEventListener('submit', event => {
  input.value = input.value.trim();
  if (!input.value) { event.preventDefault(); input.reportValidity(); }
});
// Keep video playback identical to the reference: the player replaces its poster inline.
const play = document.querySelector('.video-section__play');
play.addEventListener('click', () => {
  const iframe = document.createElement('iframe');
  iframe.src = `${play.dataset.src}&autoplay=1`;
  iframe.title = 'USJunkCars company and service video';
  iframe.allow = 'autoplay; fullscreen; picture-in-picture';
  iframe.allowFullscreen = true;
  iframe.className = 'clone-video-player';
  document.querySelector('.video-section').classList.add('playing');
  play.parentElement.append(iframe);
  iframe.focus();
  play.hidden = true;
}, {once: true});
// Review carousel, with keyboard and touch controls and only the active review exposed.
const reviews = document.querySelector('.testimonials-slider');
const reviewSlides = [...reviews.querySelectorAll('.testimonials-slider__item')];
const reviewPagination = reviews.querySelector('.swiper-pagination');
reviews.setAttribute('role', 'region');
reviews.setAttribute('aria-label', 'Customer reviews');
reviews.setAttribute('aria-roledescription', 'carousel');
let reviewIndex = 0;
const dots = reviewSlides.map((slide, index) => {
  const dot = document.createElement('button');
  dot.type = 'button'; dot.className = 'swiper-pagination-bullet';
  dot.setAttribute('aria-label', `Show review ${index + 1}`);
  dot.addEventListener('click', () => showReview(index));
  reviewPagination.append(dot);
  slide.setAttribute('role', 'group');
  slide.setAttribute('aria-label', `${index + 1} of ${reviewSlides.length}`);
  return dot;
});
function showReview(index) {
  reviewIndex = (index + reviewSlides.length) % reviewSlides.length;
  reviewSlides.forEach((slide, i) => { slide.hidden = i !== reviewIndex; });
  dots.forEach((dot, i) => {
    dot.classList.toggle('swiper-pagination-bullet-active', i === reviewIndex);
    dot.setAttribute('aria-current', String(i === reviewIndex));
  });
}
reviews.querySelector('.testimonials-slider__prev').addEventListener('click', () => showReview(reviewIndex - 1));
reviews.querySelector('.testimonials-slider__next').addEventListener('click', () => showReview(reviewIndex + 1));
reviews.addEventListener('keydown', event => {
  if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
    event.preventDefault(); showReview(reviewIndex + (event.key === 'ArrowRight' ? 1 : -1));
  }
});
let touchStart = null;
reviews.addEventListener('touchstart', event => { touchStart = event.touches[0].clientX; }, {passive: true});
reviews.addEventListener('touchend', event => {
  if (touchStart === null) return;
  const delta = event.changedTouches[0].clientX - touchStart;
  if (Math.abs(delta) > 50) showReview(reviewIndex + (delta < 0 ? 1 : -1));
  touchStart = null;
}, {passive: true});
showReview(0);
// Native scrolling keeps every brand accessible by touch, keyboard and pagination.
const brands = document.querySelector('.brands-slider');
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
// Map names are available on both hover and keyboard focus.
document.querySelectorAll('.map svg a').forEach(link => {
  const state = link.querySelector('[data-state]')?.getAttribute('data-state') || link.getAttribute('data-state') || new URL(link.href.baseVal, location.href).pathname.slice(1).replaceAll('-', ' ');
  link.setAttribute('aria-label', state.replace(/\b\w/g, c => c.toUpperCase()));
  if (!link.querySelector('title')) {
    const title = document.createElementNS('http://www.w3.org/2000/svg', 'title');
    title.textContent = state; link.prepend(title);
  }
});
const banner = document.querySelector('.report-banner');
const bannerKey = 'usjunkcars-promotion-dismissed';
try { banner.hidden = sessionStorage.getItem(bannerKey) === 'yes'; } catch { /* Storage is optional. */ }
function updateBannerSpace() {
  const height = banner.hidden ? 0 : banner.getBoundingClientRect().height;
  document.documentElement.style.setProperty('--report-banner-height', `${height}px`);
}
banner.querySelector('button').addEventListener('click', () => {
  banner.hidden = true;
  try { sessionStorage.setItem(bannerKey, 'yes'); } catch { /* Storage is optional. */ }
  updateBannerSpace();
});
new ResizeObserver(updateBannerSpace).observe(banner);
updateBannerSpace();
