"""Generate original background artwork: hero board (red), CTA banner (blue) and a waving US flag.

Writes SVG sources to apps/web/public/images/backgrounds/; scripts/render-backgrounds.cjs encodes them.
Run: python3 scripts/build-backgrounds.py
"""
import math, pathlib

OUT = pathlib.Path(__file__).resolve().parents[1] / 'apps/web/public/images/backgrounds'
OUT.mkdir(parents=True, exist_ok=True)


def tire_track(points, width, opacity, color='#FFFFFF'):
    """A tread trail: short perpendicular bars along a smooth path."""
    bars = []
    for (x1, y1), (x2, y2) in zip(points, points[1:]):
        dx, dy = x2 - x1, y2 - y1
        length = math.hypot(dx, dy) or 1
        nx, ny = -dy / length * width / 2, dx / length * width / 2
        bars.append(f'M{x1 - nx:.1f} {y1 - ny:.1f}L{x1 + nx:.1f} {y1 + ny:.1f}')
    return f'<path d="{" ".join(bars)}" stroke="{color}" stroke-width="5" stroke-linecap="round" opacity="{opacity}"/>'


def curve(x0, y0, x1, y1, bend, n=46):
    pts = []
    for i in range(n + 1):
        t = i / n
        pts.append((x0 + (x1 - x0) * t + bend * math.sin(math.pi * t), y0 + (y1 - y0) * t))
    return pts


# Hero board, 1140x1170 (2x of 570x585)
hero = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1140" height="1170" viewBox="0 0 1140 1170">
<defs>
<linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#F45C74"/><stop offset=".55" stop-color="#DE193E"/><stop offset="1" stop-color="#A10E2C"/></linearGradient>
<radialGradient id="h" cx=".28" cy=".18" r=".7"><stop offset="0" stop-color="#FFFFFF" stop-opacity=".28"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></radialGradient>
</defs>
<rect width="1140" height="1170" fill="url(#g)"/><rect width="1140" height="1170" fill="url(#h)"/>
{tire_track(curve(1260, 260, 160, 1300, -260), 46, .10)}
{tire_track(curve(1300, 330, 230, 1330, -260), 46, .10)}
<path d="M0 1170L1140 640V1170z" fill="#7E0A22" opacity=".18"/>
</svg>'''

# CTA banner, 2342x706 (2x of 1171x353)
banner = f'''<svg xmlns="http://www.w3.org/2000/svg" width="2342" height="706" viewBox="0 0 2342 706">
<defs>
<linearGradient id="g" x1="0" y1="0" x2="1" y2=".4"><stop offset="0" stop-color="#2F7BEA"/><stop offset=".5" stop-color="#0953B8"/><stop offset="1" stop-color="#0A2B5E"/></linearGradient>
<radialGradient id="h" cx=".2" cy=".1" r=".6"><stop offset="0" stop-color="#FFFFFF" stop-opacity=".22"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></radialGradient>
</defs>
<rect width="2342" height="706" fill="url(#g)"/><rect width="2342" height="706" fill="url(#h)"/>
{tire_track(curve(700, -60, 1500, 780, 360), 44, .08)}
{tire_track(curve(770, -60, 1570, 780, 360), 44, .08)}
<g stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" opacity=".10"><path d="M1900 120h300M1840 170h360M1960 220h240"/></g>
</svg>'''

# Waving US flag, 880x512 (2x of 440x256), transparent background
W, H, PAD = 880, 512, 40
stripe_h = (H - 2 * PAD - 40) / 13


def wave(x):
    return 18 * math.sin((x - PAD) / (W - 2 * PAD) * 2 * math.pi * 1.1)


def band(y_top, y_bot, x0, x1, n=60):
    top = [(x0 + (x1 - x0) * i / n, y_top) for i in range(n + 1)]
    pts = [(x, y + wave(x)) for x, y in top] + [(x, y_bot + wave(x)) for x, _ in reversed(top)]
    return 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pts) + 'Z'


shade = []
for i in range(13):
    y0 = PAD + 20 + i * stripe_h
    shade.append(f'<path d="{band(y0, y0 + stripe_h + .6, PAD, W - PAD)}" fill="{"#DE193E" if i % 2 == 0 else "#FFFFFF"}"/>')
canton_w, canton_h = (W - 2 * PAD) * .4, stripe_h * 7
stars = []
for r in range(9):
    for c in range(11 if r % 2 == 0 else 10):
        if (r % 2 == 0 and c % 2 == 0) or (r % 2 == 1 and c % 2 == 1) or True:
            pass
for r in range(9):
    cols = 6 if r % 2 == 0 else 5
    for c in range(cols):
        x = PAD + canton_w * ((c * 2 + (1 if r % 2 else 0) + 1) / 12)
        y = PAD + 20 + canton_h * ((r + 1) / 10) + wave(x)
        pts = []
        for k in range(10):
            ang = -math.pi / 2 + k * math.pi / 5
            rad = 7 if k % 2 == 0 else 2.9
            pts.append(f'{x + rad * math.cos(ang):.1f} {y + rad * math.sin(ang):.1f}')
        stars.append('M' + ' L'.join(pts) + 'Z')
light = []
for i in range(6):
    x = PAD + (W - 2 * PAD) * (i + .5) / 6
    light.append(f'<rect x="{x - 40:.0f}" y="0" width="80" height="{H}" fill="#{"000000" if i % 2 else "FFFFFF"}" opacity="{.06 if i % 2 else .1}"/>')
flag = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs><clipPath id="c"><path d="{band(PAD + 20, PAD + 20 + 13 * stripe_h, PAD, W - PAD)}"/></clipPath></defs>
<g clip-path="url(#c)">{"".join(shade)}
<path d="{band(PAD + 20, PAD + 20 + canton_h, PAD, PAD + canton_w)}" fill="#0A2B5E"/>
<path d="{" ".join(stars)}" fill="#FFFFFF"/>
{"".join(light)}</g>
</svg>'''

for name, text in [('hero-board-red.svg', hero), ('cta-banner-blue.svg', banner), ('usa-flag-nationwide.svg', flag)]:
    (OUT / name).write_text(text)
print('wrote backgrounds to', OUT)


# ---------------------------------------------------------------- Animated waving flag
# Same artwork as the still flag, animated with SMIL so it also plays inside an <img>.
# The wave is pinned at the left (pole) edge and grows toward the free end.
FRAMES, DUR, N = 16, 2.6, 18
x0f, x1f = PAD, W - PAD
top0 = PAD + 20


def wave_t(x, phase):
    k = (x - x0f) / (x1f - x0f)
    return (6 + 22 * k) * math.sin(k * 2 * math.pi * 1.15 - phase) - 6 * k


def band_t(y_top, y_bot, xa, xb, phase):
    xs = [xa + (xb - xa) * i / N for i in range(N + 1)]
    pts = [(x, y_top + wave_t(x, phase)) for x in xs] + [(x, y_bot + wave_t(x, phase)) for x in reversed(xs)]
    return 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pts) + 'Z'


def anim(frames):
    values = ';'.join(frames + frames[:1])
    return f'<animate attributeName="d" dur="{DUR}s" repeatCount="indefinite" calcMode="linear" values="{values}"/>'


phases = [2 * math.pi * f / FRAMES for f in range(FRAMES)]
parts = []
for i in range(13):
    y0 = top0 + i * stripe_h
    frames = [band_t(y0, y0 + stripe_h + .6, x0f, x1f, p) for p in phases]
    parts.append(f'<path fill="{"#DE193E" if i % 2 == 0 else "#FFFFFF"}" d="{frames[0]}">{anim(frames)}</path>')
canton = [band_t(top0, top0 + canton_h, x0f, x0f + canton_w, p) for p in phases]
parts.append(f'<path fill="#0A2B5E" d="{canton[0]}">{anim(canton)}</path>')


def star_d(x, y):
    return 'M' + ' L'.join(f'{x + (7 if k % 2 == 0 else 2.9) * math.cos(-math.pi / 2 + k * math.pi / 5):.1f} '
                           f'{y + (7 if k % 2 == 0 else 2.9) * math.sin(-math.pi / 2 + k * math.pi / 5):.1f}' for k in range(10)) + 'Z'


# Stars in one column share an x position, so each column moves as a group.
columns = {}
for r in range(9):
    for c in range(6 if r % 2 == 0 else 5):
        x = x0f + canton_w * ((c * 2 + (1 if r % 2 else 0) + 1) / 12)
        columns.setdefault(round(x, 1), []).append(star_d(x, top0 + canton_h * ((r + 1) / 10)))
for x, stars in columns.items():
    shifts = ';'.join(f'0 {wave_t(x, p):.1f}' for p in phases + phases[:1])
    parts.append(f'<g fill="#FFFFFF"><path d="{" ".join(stars)}"/>'
                 f'<animateTransform attributeName="transform" type="translate" dur="{DUR}s" repeatCount="indefinite" values="{shifts}"/></g>')

# Moving light and shadow sell the folds: a soft band that travels with the wave.
shade_id = 'fold'
shading = (f'<linearGradient id="{shade_id}" x1="0" y1="0" x2="1" y2="0" gradientUnits="objectBoundingBox">'
           f'<stop offset="0" stop-color="#000" stop-opacity="0"/><stop offset=".2" stop-color="#FFF" stop-opacity=".22"/>'
           f'<stop offset=".4" stop-color="#000" stop-opacity=".14"/><stop offset=".6" stop-color="#FFF" stop-opacity=".2"/>'
           f'<stop offset=".8" stop-color="#000" stop-opacity=".14"/><stop offset="1" stop-color="#FFF" stop-opacity=".18"/>'
           f'<animate attributeName="x1" dur="{DUR}s" repeatCount="indefinite" values="0;-.36;0"/>'
           f'<animate attributeName="x2" dur="{DUR}s" repeatCount="indefinite" values="1;.64;1"/></linearGradient>')
outline = [band_t(top0, top0 + 13 * stripe_h, x0f, x1f, p) for p in phases]
parts.append(f'<path fill="url(#{shade_id})" d="{outline[0]}">{anim(outline)}</path>')

waving = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
          f'aria-label="US flag waving"><title>US flag waving</title><defs>{shading}</defs>{"".join(parts)}</svg>')
(OUT / 'usa-flag-waving.svg').write_text(waving)
print('wrote animated flag', round(len(waving) / 1024), 'KB')
