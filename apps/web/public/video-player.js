// Homepage launch video: a muted inline preview that loops while visible, and a full-screen player
// with sound, tap to mute, volume, seek and close. Videos are served from this site (no YouTube embed),
// so visitors stay on usjunkcars.si.
(() => {
  const card = document.querySelector('[data-launch-video]');
  if (!card) return;

  const preview = card.querySelector('video');
  const dataLayer = (window.dataLayer = window.dataLayer || []);
  const track = (event, extra) => dataLayer.push({ event, video_title: 'USJunkCars launch', ...extra });
  const calm = matchMedia('(prefers-reduced-motion: reduce)').matches || navigator.connection?.saveData;

  // The poster is a card background that is only attached once the card is within ~1.5 screens,
  // so it does not compete with the hero image on first load.
  if ('IntersectionObserver' in window) {
    const near = new IntersectionObserver(([entry]) => {
      if (!entry.isIntersecting) return;
      card.classList.add('is-near');
      near.disconnect();
    }, { rootMargin: '150% 0px' });
    near.observe(card);
  } else card.classList.add('is-near');

  // Inline preview: play only while on screen, never with sound.
  if (!calm && 'IntersectionObserver' in window) {
    new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        if (!preview.src) preview.src = preview.dataset.src;
        preview.play().catch(() => {});
      } else preview.pause();
    }, { threshold: 0.35 }).observe(preview);
  }

  // Full-screen player, built once on first open.
  let modal, video, muteBtn, volume, playBtn, bar, fill, timeEl, hideTimer, lastProgress = 0;
  const fmt = s => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, '0')}`;
  const icon = name => `<svg viewBox="0 0 24 24" aria-hidden="true"><use href="#lv-${name}"></use></svg>`;

  function build() {
    modal = document.createElement('div');
    modal.className = 'lv-modal';
    modal.setAttribute('role', 'dialog');
    modal.setAttribute('aria-modal', 'true');
    modal.setAttribute('aria-label', 'USJunkCars video');
    modal.innerHTML = `
<svg width="0" height="0" style="position:absolute">
  <symbol id="lv-play" viewBox="0 0 24 24"><path fill="currentColor" d="M8 5.5v13l11-6.5z"/></symbol>
  <symbol id="lv-pause" viewBox="0 0 24 24"><path fill="currentColor" d="M7 5h3.5v14H7zM13.5 5H17v14h-3.5z"/></symbol>
  <symbol id="lv-sound" viewBox="0 0 24 24"><path fill="currentColor" d="M4 9h4l5-4v14l-5-4H4z"/><path d="M16 8.5a5 5 0 0 1 0 7M18.5 6a8.5 8.5 0 0 1 0 12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></symbol>
  <symbol id="lv-muted" viewBox="0 0 24 24"><path fill="currentColor" d="M4 9h4l5-4v14l-5-4H4z"/><path d="M16.5 9.5l5 5m0-5l-5 5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></symbol>
  <symbol id="lv-close" viewBox="0 0 24 24"><path d="M6 6l12 12M18 6L6 18" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/></symbol>
</svg>
<video class="lv-video" playsinline preload="auto"></video>
<button class="lv-close" type="button" aria-label="Close video">${icon('close')}</button>
<button class="lv-tap" type="button" aria-label="Mute">${icon('sound')}<span>Tap to mute</span></button>
<div class="lv-controls">
  <button class="lv-btn lv-play" type="button" aria-label="Pause">${icon('pause')}</button>
  <div class="lv-bar" role="slider" tabindex="0" aria-label="Seek" aria-valuemin="0" aria-valuemax="100"><div class="lv-fill"></div></div>
  <span class="lv-time">0:00</span>
  <button class="lv-btn lv-mute" type="button" aria-label="Mute">${icon('sound')}</button>
  <input class="lv-volume" type="range" min="0" max="1" step="0.05" value="1" aria-label="Volume">
</div>`;
    document.body.appendChild(modal);
    video = modal.querySelector('.lv-video');
    muteBtn = modal.querySelector('.lv-mute');
    volume = modal.querySelector('.lv-volume');
    playBtn = modal.querySelector('.lv-play');
    bar = modal.querySelector('.lv-bar');
    fill = modal.querySelector('.lv-fill');
    timeEl = modal.querySelector('.lv-time');
    const tap = modal.querySelector('.lv-tap');

    const syncSound = () => {
      const off = video.muted || video.volume === 0;
      const name = off ? 'muted' : 'sound';
      muteBtn.innerHTML = icon(name);
      muteBtn.setAttribute('aria-label', off ? 'Unmute' : 'Mute');
      tap.innerHTML = `${icon(name)}<span>${off ? 'Tap to unmute' : 'Tap to mute'}</span>`;
      tap.setAttribute('aria-label', off ? 'Unmute' : 'Mute');
      volume.value = off ? 0 : video.volume;
      volume.style.setProperty('--v', `${volume.value * 100}%`);
    };
    const toggleMute = () => {
      if (video.muted || video.volume === 0) { video.muted = false; if (video.volume === 0) video.volume = 1; }
      else video.muted = true;
      syncSound();
      track(video.muted ? 'video_mute' : 'video_unmute');
    };
    const syncPlay = () => {
      playBtn.innerHTML = icon(video.paused ? 'play' : 'pause');
      playBtn.setAttribute('aria-label', video.paused ? 'Play' : 'Pause');
    };

    tap.addEventListener('click', e => { e.stopPropagation(); toggleMute(); wake(); });
    muteBtn.addEventListener('click', toggleMute);
    volume.addEventListener('input', () => {
      video.volume = Number(volume.value);
      video.muted = video.volume === 0;
      syncSound();
    });
    playBtn.addEventListener('click', () => (video.paused ? video.play() : video.pause()));
    // Tapping the picture itself toggles sound, as the on-screen hint says.
    video.addEventListener('click', () => { toggleMute(); wake(); });
    video.addEventListener('play', syncPlay);
    video.addEventListener('pause', syncPlay);
    video.addEventListener('volumechange', syncSound);
    video.addEventListener('timeupdate', () => {
      const k = video.duration ? video.currentTime / video.duration : 0;
      fill.style.width = `${k * 100}%`;
      bar.setAttribute('aria-valuenow', Math.round(k * 100));
      timeEl.textContent = `${fmt(video.currentTime)} / ${fmt(video.duration || 57)}`;
      for (const q of [25, 50, 75]) if (k * 100 >= q && lastProgress < q) { lastProgress = q; track('video_progress', { video_percent: q }); }
    });
    video.addEventListener('ended', () => { track('video_complete'); close(); });

    const seek = e => {
      const r = bar.getBoundingClientRect();
      video.currentTime = Math.min(1, Math.max(0, (e.clientX - r.left) / r.width)) * (video.duration || 0);
    };
    bar.addEventListener('pointerdown', e => { bar.setPointerCapture(e.pointerId); seek(e); bar.onpointermove = seek; });
    bar.addEventListener('pointerup', () => { bar.onpointermove = null; });
    bar.addEventListener('keydown', e => {
      if (e.key === 'ArrowRight') video.currentTime += 5;
      if (e.key === 'ArrowLeft') video.currentTime -= 5;
    });

    modal.querySelector('.lv-close').addEventListener('click', close);
    modal.addEventListener('pointermove', wake);
    document.addEventListener('keydown', e => {
      if (!modal.classList.contains('is-open')) return;
      if (e.key === 'Escape') close();
      if (e.key === ' ' && e.target === document.body) { e.preventDefault(); video.paused ? video.play() : video.pause(); }
      if (e.key === 'm') toggleMute();
    });
    document.addEventListener('fullscreenchange', () => { if (!document.fullscreenElement && modal.classList.contains('is-open')) close(); });
    syncSound();
  }

  // Controls fade out after a few seconds without interaction.
  function wake() {
    modal.classList.remove('is-idle');
    clearTimeout(hideTimer);
    hideTimer = setTimeout(() => !video.paused && modal.classList.add('is-idle'), 2600);
  }

  function open() {
    if (!modal) build();
    if (modal.classList.contains('is-open')) return;
    // Phones held upright get the vertical cut; everything else the 16:9 film.
    const upright = matchMedia('(orientation: portrait) and (max-width: 820px)').matches;
    const src = upright ? card.dataset.vertical : card.dataset.full;
    if (video.getAttribute('src') !== src) video.src = src;
    video.currentTime = 0;
    video.muted = false;
    lastProgress = 0;
    modal.classList.toggle('is-vertical', upright);
    modal.classList.add('is-open');
    document.documentElement.classList.add('lv-lock');
    preview.pause();
    modal.requestFullscreen?.().catch(() => {});
    // Sound on by default (the click is a user gesture); fall back to muted if the browser refuses.
    video.play().catch(() => { video.muted = true; video.play().catch(() => {}); });
    track('video_open', { video_variant: upright ? 'vertical' : 'horizontal' });
    wake();
    modal.querySelector('.lv-tap').focus({ preventScroll: true });
  }

  function close() {
    if (!modal || !modal.classList.contains('is-open')) return;
    modal.classList.remove('is-open');
    document.documentElement.classList.remove('lv-lock');
    video.pause();
    if (document.fullscreenElement) document.exitFullscreen().catch(() => {});
    if (!calm) preview.play().catch(() => {});
    card.querySelector('.lv-card__open').focus({ preventScroll: true });
  }

  card.querySelector('.lv-card__open').addEventListener('click', open);
})();
