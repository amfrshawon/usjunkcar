"""Generate the US Junk Cars icon set (original artwork in brand colors).

Writes SVGs to apps/web/public/images/icons/. Run: python3 scripts/build-icons.py
Navy line-art cars with a red symbol per condition, navy documents for titles and paperwork,
and solid Pickup Blue silhouettes for vehicle types.
"""
import pathlib

OUT = pathlib.Path(__file__).resolve().parents[1] / 'apps/web/public/images/icons'
OUT.mkdir(parents=True, exist_ok=True)
NAVY, BLUE, RED, WHITE = '#0A2B5E', '#0953B8', '#DE193E', '#FFFFFF'
LINE = f'fill="none" stroke="{NAVY}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"'
ACC = f'fill="none" stroke="{RED}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"'


def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{title}"><title>{title}</title>{body}</svg>\n')


def car(dy=0, extra=''):
    """Line-art sedan in a 72x72 box, sitting low so a symbol fits above it."""
    return (f'<g transform="translate(0 {dy})" {extra}>'
            f'<path {LINE} d="M7 50v-6.5c0-2.6 1.6-4.3 4.2-4.8l7.8-1.5 8.4-8.6c1.3-1.3 3-2 4.8-2h12.4c1.9 0 3.6.8 4.8 2.2l6.6 8 5.6 1.1c2.6.5 4.4 2.6 4.4 5.2V50"/>'
            f'<path {LINE} d="M23 38.2l6.2-6.2c.9-.9 2.1-1.4 3.3-1.4h11.3c1.3 0 2.5.6 3.3 1.6l4.5 6"/>'
            f'<path {LINE} d="M7 50h7.2M27.8 50h16.4M58 50h7"/>'
            f'<circle cx="21" cy="50.5" r="5.4" {LINE}/><circle cx="51" cy="50.5" r="5.4" {LINE}/></g>')


def badge(inner, cx=55, cy=16, r=10):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{RED}"/><g fill="none" stroke="{WHITE}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">{inner}</g>'


def doc(dashed=False):
    dash = ' stroke-dasharray="4 3.2"' if dashed else ''
    return (f'<path {LINE}{dash} d="M17 9h28l10 10v44a3 3 0 0 1-3 3H17a3 3 0 0 1-3-3V12a3 3 0 0 1 3-3z"/>'
            + ('' if dashed else f'<path {LINE} d="M45 9v10h10M22 28h18M22 35h24M22 42h14"/>'))


CONDITIONS = {
    # file name: (title, svg body)
    'biohazard': ('Biohazard or chemical damage', car(6) + f'<path fill="{RED}" d="M55 5.5l10.5 18.5h-21z"/><path fill="none" stroke="{WHITE}" stroke-width="2.4" stroke-linecap="round" d="M55 11.5v6"/><circle cx="55" cy="21" r="1.4" fill="{WHITE}"/>'),
    'blown-engine': ('Blown engine', car(6) + f'<path {ACC} d="M50 26c-3-3 3-5 0-8s3-5 0-8M57 26c-3-3 3-5 0-8s3-5 0-8"/>'),
    'broken-transmission': ('Broken transmission', f'<path {LINE} d="M20 14v38M36 14v38M52 14v20M20 33h32"/><circle cx="20" cy="12" r="4" {LINE}/><circle cx="36" cy="12" r="4" {LINE}/><circle cx="52" cy="12" r="4" {LINE}/>' + badge('<path d="M51 47l8 8M59 47l-8 8"/>', 55, 51, 10)),
    'burned': ('Burned car', car(6) + f'<path fill="{RED}" d="M53 30c-6 0-9-4-9-9 0-4 3-6 4-11 2 3 3 4 3 7 2-1 3-4 3-7 5 4 8 8 8 12 0 5-3 8-9 8z"/>'),
    'damaged': ('Damaged car', car(6) + f'<path {ACC} d="M30 37l5 5-4 4 6 5M44 9l2 6 6-2-3 6"/>'),
    'flooded': ('Flooded car', car(-4) + f'<path fill="none" stroke="{BLUE}" stroke-width="2.6" stroke-linecap="round" d="M5 56c4-3 8-3 12 0s8 3 12 0 8-3 12 0 8 3 12 0 8-3 14 0M5 64c4-3 8-3 12 0s8 3 12 0 8-3 12 0 8 3 12 0 8-3 14 0"/>'),
    'frame-damage': ('Frame damage', car(6) + f'<path {ACC} d="M10 64l18-6 16 6 18-6"/>'),
    'hail': ('Hail damage', car(8) + f'<g fill="{RED}"><circle cx="18" cy="12" r="3"/><circle cx="34" cy="7" r="3"/><circle cx="50" cy="13" r="3"/><circle cx="62" cy="6" r="3"/><circle cx="27" cy="21" r="2.4"/><circle cx="44" cy="22" r="2.4"/></g>'),
    'junk-car-for-cash': ('Junk car for cash', car(6) + badge('<path d="M58 11.5h-4.5a2.5 2.5 0 0 0 0 5h3a2.5 2.5 0 0 1 0 5H51M55 8.5v2.5M55 21.5v2.5"/>', 55, 16, 11)),
    'mechanical-problems': ('Mechanical problems', car(6) + f'<path {ACC} d="M61.6 8.4a6 6 0 0 0-8.1 7.4l-7.3 7.3a2.3 2.3 0 0 0 3.2 3.2l7.3-7.3a6 6 0 0 0 7.4-8.1l-3.6 3.6-3-.5-.5-3z"/>'),
    'no-engine': ('Car without engine', f'<path {LINE} d="M16 26h8v-5h16v5h10l6 6h5v14h-5l-6 6H24l-4-4h-4z"/><path {LINE} d="M10 32v14M16 39h-6"/>' + badge('<path d="M50 11l10 10M60 11L50 21"/>')),
    'non-running': ('Non-running car', car(6) + badge('<path d="M55 9.5v6.5M50.3 12.3a7 7 0 1 0 9.4 0"/>')),
    'old-car': ('Old car', f'<g transform="translate(0 6)"><path {LINE} d="M8 46v-8h8l4-14h22l6 14h14v8"/><path {LINE} d="M24 24v14M38 24v14M8 46h6M28 46h16M58 46h6"/><circle cx="21" cy="47" r="6" {LINE}/><circle cx="51" cy="47" r="6" {LINE}/></g>' + badge('<path d="M55 10v6l4 2"/>')),
    'salvage': ('Salvage car', car(6) + f'<path {ACC} d="M48 10a8 8 0 0 1 13 2M62 7v5h-5M62 22a8 8 0 0 1-13-2M48 25v-5h5"/>'),
    'scrap': ('Scrap car', f'<path {LINE} d="M10 44h52v12H10zM16 44l6-8h28l6 8"/><path {LINE} d="M22 50h28"/><path {ACC} d="M24 8v14M24 22l-5-5M24 22l5-5M48 8v14M48 22l-5-5M48 22l5-5"/>'),
    'totaled': ('Totaled car', car(6) + badge('<path d="M51 12l8 8M59 12l-8 8"/>')),
    'used-car': ('Used car', car(6) + f'<path fill="{RED}" d="M46 8h12l7 7-11 11-8-8z"/><circle cx="57" cy="12" r="2" fill="{WHITE}"/>'),
    'vandalized': ('Vandalized car', car(6) + f'<path {ACC} d="M30 42c3-4 6 4 9 0s6 4 9 0"/><rect x="52" y="8" width="9" height="14" rx="2" fill="{RED}"/><path {ACC} d="M54 4h5M50 26l-4 4"/>'),
    'without-catalytic-converter': ('Car without catalytic converter', f'<rect x="14" y="32" width="36" height="18" rx="9" {LINE}/><path {LINE} d="M6 41h8M50 41h12M24 38v6M32 38v6M40 38v6"/>' + badge('<path d="M50 11l10 10M60 11L50 21"/>')),
    'without-transmission': ('Car without transmission', f'<circle cx="30" cy="40" r="7" {LINE}/><path {LINE} d="M30 24v5M30 51v5M14 40h5M41 40h5M18.7 28.7l3.5 3.5M37.8 47.8l3.5 3.5M18.7 51.3l3.5-3.5M37.8 32.2l3.5-3.5"/>' + badge('<path d="M50 11l10 10M60 11L50 21"/>')),
    'without-inspection': ('Car without inspection', f'<circle cx="30" cy="32" r="16" {LINE}/><path {LINE} d="M42 44l14 14"/><path {ACC} d="M24 26l12 12M36 26L24 38"/>'),
    'wrecked': ('Wrecked car', car(6) + f'<path fill="{RED}" d="M60 22l-3.5-4.5-5.4 1.8 1.3-5.6-5-3 5.6-1.2.4-5.7 4 4 5-2.5-1 5.6 5 2.8-5.6 1.4z"/>'),
}

TITLES = {
    'clean-title': ('Clean title', doc() + badge('<path d="M50.5 54l3.3 3.3 6.7-6.7"/>', 55, 54, 10).replace(RED, BLUE)),
    'without-title': ('Car without title', doc(dashed=True) + f'<path {ACC} d="M29.5 31a5.5 5.5 0 1 1 7.7 5c-1.6.7-2.7 2.3-2.7 4v1.5"/><circle cx="34.5" cy="49" r="1.8" fill="{RED}"/>'),
    'salvage-title': ('Salvage title', doc() + badge('<path d="M51.5 50.5a5 5 0 0 1 7.5 1.2M59.5 49v3.4h-3.4M58.5 57.5a5 5 0 0 1-7.5-1.2M50.5 59v-3.4h3.4"/>', 55, 54, 10)),
    'non-repairable-title': ('Non-repairable title', doc() + badge('<path d="M51 50l8 8M59 50l-8 8"/>', 55, 54, 10)),
}

PAPERWORK = {
    'without-license-plate': ('Car without license plate', f'<rect x="8" y="22" width="56" height="28" rx="4" {LINE} stroke-dasharray="4 3.2"/><path {ACC} d="M14 58L58 14"/>'),
    'expired-registration': ('Expired registration', doc() + badge('<path d="M55 49.5v5l3.5 2"/>', 55, 54, 10)),
    'without-registration': ('Car without registration', doc(dashed=True) + f'<path {ACC} d="M28 32l14 14M42 32L28 46"/>'),
    'with-registration': ('Car with registration', doc() + badge('<path d="M50.5 54l3.3 3.3 6.7-6.7"/>', 55, 54, 10).replace(RED, BLUE)),
}

# Vehicle silhouettes, 73x33, solid blue with white glass and navy wheels.
def body(path, glass, wheels=((17, 26), (56, 26)), r=6):
    w = ''.join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{NAVY}"/><circle cx="{x}" cy="{y}" r="{r * 0.42:.1f}" fill="{WHITE}"/>' for x, y in wheels)
    return f'<path fill="{BLUE}" d="{path}"/>' + ''.join(f'<path fill="{WHITE}" d="{g}"/>' for g in glass) + w

VEHICLES = {
    'pickup-truck': ('Pickup truck', body('M2 26v-6c0-2 1.2-3 3-3.4L30 15V6.5C30 5 31 4 32.5 4h12c1.2 0 2.2.6 2.8 1.6L52 13l14 2c2.6.4 4.5 2.4 4.5 5v6z', ['M35 7h9l3.8 6.5H35z'])),
    'convertible': ('Convertible', body('M2 26v-5c0-2 1.4-3.4 3.4-3.8L20 15l8-5.5 2 .5-5 5h18l9 3 13 1.8c2.4.4 4 2.3 4 4.7V26z', [])),
    'hatchback': ('Hatchback', body('M3 26v-9c0-1.8 1-3.4 2.6-4.2L18 6.5C19.6 5.6 21.5 5 23.4 5H40c2 0 3.8.8 5.2 2.2L52 14l13 2.2c2.6.4 4.5 2.6 4.5 5.2V26z', ['M20 8.5c1-.5 2.2-.8 3.4-.8H30v6H12z', 'M33 7.7h7c1.2 0 2.3.5 3.1 1.3l4.5 4.7H33z'])),
    'suv': ('SUV', body('M2 26v-8c0-2 1.3-3.6 3.2-4.1L10 12.6 15 4.5C15.8 3.3 17 2.6 18.4 2.6h26c1.6 0 3 .8 3.9 2.1L54 12.6l12.4 1.9c2.4.4 4.1 2.4 4.1 4.8V26z', ['M18.8 5.6H29v7H14.6z', 'M32 5.6h12.2c.8 0 1.5.4 1.9 1L50 12.6H32z'])),
    'bus': ('Bus', body('M2 26V5c0-2 1.6-3.5 3.5-3.5h58c3.5 0 6.5 3 6.5 6.5V26z', ['M6 5h9v8H6z', 'M19 5h9v8h-9z', 'M32 5h9v8h-9z', 'M45 5h9v8h-9z', 'M58 5h6.5c1.4 0 2.5 1.1 2.5 2.5V13h-9z'], wheels=((15, 27), (58, 27)))),
    'sedan': ('Sedan', body('M2 26v-6c0-2.2 1.6-4 3.8-4.4L17 13.5l8.6-7.2c1.4-1.2 3.2-1.8 5-1.8h12.2c2 0 3.8.8 5.2 2.2l6.4 6.6 11.6 2c2.6.5 4.5 2.7 4.5 5.3V26z', ['M23 13.2l4.6-4c.9-.8 2-1.2 3.2-1.2H36v5.2z', 'M39 8h4c1.2 0 2.3.5 3.1 1.3l3.8 3.9H39z'])),
    'box-truck': ('Box truck', body('M2 26V3.5C2 2.1 3.1 1 4.5 1H44v25zM46 26V9h12c1.6 0 3 .8 3.8 2.1L70 21v5z', ['M49 12h8.4c.7 0 1.3.3 1.6.9l3.6 5.6H49z'], wheels=((14, 27), (58, 27)))),
    'station-wagon': ('Station wagon', body('M2 26v-8c0-2 1.4-3.7 3.4-4L10 13l4-7.8C14.8 3.8 16.2 3 17.8 3H45c1.8 0 3.4.9 4.3 2.4L54 13l12 1.8c2.5.4 4.5 2.5 4.5 5V26z', ['M17.5 6H29v7H14z', 'M32 6h12.5c.8 0 1.5.4 1.9 1.1L50 13H32z'])),
    'van': ('Van', body('M2 26V6.5C2 4 4 2 6.5 2H47c2 0 3.8 1 4.9 2.6l6.6 9.4 9 2c2 .5 3.5 2.3 3.5 4.4V26z', ['M44 5.5h3.6c.9 0 1.7.4 2.2 1.1l5 7.4H44z'])),
    'rv-motorhome': ('RV or motorhome', body('M2 26V5c0-2.2 1.8-4 4-4h48c2 0 3.6 1.4 3.9 3.3l1.3 7.7h4.3c2.6 0 4.7 1.9 5.1 4.4L70 26z', ['M7 6h10v6H7z', 'M22 6h10v6H22z', 'M57 13h4.5c1.4 0 2.6 1 2.9 2.4l.6 3.6H57z'], wheels=((15, 27), (56, 27)))),
    'coupe': ('Coupe', body('M2 26v-6c0-2.2 1.6-4 3.8-4.4L19 13l9.4-6.3c1.5-1 3.3-1.6 5.1-1.6h9.6c2.2 0 4.3 1 5.7 2.7L54 14l11.8 2.1c2.6.5 4.7 2.7 4.7 5.3V26z', ['M25.5 13l4.6-3.2c1-.7 2.2-1 3.4-1H38V13z', 'M41 8.8h2.2c1.4 0 2.6.6 3.5 1.7L49.5 13H41z'])),
}

# Section icons (keep the original viewBox sizes so the layout is unchanged).
SECTION = {
    # The three step icons sit on red tiles, so they are white.
    'instant-offer': (40, 26, 'Instant offer', f'<rect x="1.5" y="1.5" width="37" height="23" rx="4" fill="none" stroke="{WHITE}" stroke-width="2.4"/><path fill="{WHITE}" d="M22.5 4.5l-9 10h6l-2.5 7 9-10h-6z"/>'),
    'schedule-pickup': (36, 41, 'Schedule a free pickup', f'<rect x="2" y="6" width="32" height="32" rx="4" fill="none" stroke="{WHITE}" stroke-width="2.6"/><path fill="none" stroke="{WHITE}" stroke-width="2.6" stroke-linecap="round" d="M2 15h32M11 2v7M25 2v7"/><path fill="none" stroke="{WHITE}" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round" d="M11 26.5l5 5 9.5-9.5"/>'),
    'get-paid': (42, 32, 'Get paid on the spot', f'<rect x="1.5" y="5" width="39" height="22" rx="3" fill="none" stroke="{WHITE}" stroke-width="2.4"/><circle cx="21" cy="16" r="6" fill="none" stroke="{WHITE}" stroke-width="2.4"/><path fill="none" stroke="{WHITE}" stroke-width="2.4" stroke-linecap="round" d="M7 10.5v0M35 21.5v0"/>'),
    'offer-in-minutes': (48, 47, 'Offer in minutes', f'<circle cx="24" cy="25" r="19" fill="none" stroke="{NAVY}" stroke-width="2.8"/><path fill="none" stroke="{RED}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" d="M24 13v12l8 5"/><path fill="none" stroke="{NAVY}" stroke-width="2.8" stroke-linecap="round" d="M18 2h12"/>'),
    'any-condition': (48, 47, 'Any condition accepted', f'<path fill="none" stroke="{NAVY}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" d="M4 37v-5c0-1.8 1.2-3.1 3-3.5l5-1 6-6.2c.9-.9 2.1-1.4 3.4-1.4h8.5c1.3 0 2.5.6 3.4 1.6l4.9 6 3.6.7c1.8.4 3.2 1.8 3.2 3.7V37M4 37h4.5M17.5 37h12.5M39 37h5"/><circle cx="13" cy="37.5" r="4.2" fill="none" stroke="{NAVY}" stroke-width="2.6"/><circle cx="34.5" cy="37.5" r="4.2" fill="none" stroke="{NAVY}" stroke-width="2.6"/><circle cx="38" cy="10" r="8" fill="{RED}"/><path fill="none" stroke="{WHITE}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" d="M34.5 10l2.5 2.5 4.5-4.5"/>'),
    'paid-at-pickup': (48, 47, 'Paid at pickup', f'<path fill="none" stroke="{NAVY}" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round" d="M3 33h9l9 3h10c2 0 2-3 0-3h-7M12 41h6l10 3 15-7c2-1 1-4-1-3.5L31 37"/><circle cx="30" cy="14" r="10" fill="none" stroke="{RED}" stroke-width="2.8"/><path fill="none" stroke="{RED}" stroke-width="2.4" stroke-linecap="round" d="M33 10.5h-4a2 2 0 0 0 0 4h2a2 2 0 0 1 0 4h-4M30 8v2M30 18.5v2"/>'),
    'free-towing': (48, 47, 'Free towing, no fees', f'<path fill="none" stroke="{NAVY}" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round" d="M3 35V22h12l5 6h6v7M26 35h19V25H26M15 22V12l14-6M29 6v8"/><path fill="none" stroke="{RED}" stroke-width="2.8" stroke-linecap="round" d="M29 14a3 3 0 1 0 3 3"/><circle cx="11" cy="36" r="4" fill="none" stroke="{NAVY}" stroke-width="2.8"/><circle cx="37" cy="36" r="4" fill="none" stroke="{NAVY}" stroke-width="2.8"/>'),
    'no-hidden-fees': (22, 21, 'No hidden fees', f'<path fill="{BLUE}" d="M11 .8l2.6 2.3 3.4-.4.8 3.4 3 1.7-1.4 3.2 1.4 3.2-3 1.7-.8 3.4-3.4-.4L11 20.2l-2.6-2.3-3.4.4-.8-3.4-3-1.7L2.6 10 1.2 6.8l3-1.7.8-3.4 3.4.4z"/><path fill="none" stroke="{WHITE}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M7 10.5l2.7 2.7L15 8"/>'),
}

count = 0
for group in (CONDITIONS, TITLES, PAPERWORK):
    for name, (title, inner) in group.items():
        (OUT / f'{name}.svg').write_text(svg(72, 72, inner, title)); count += 1
for name, (title, inner) in VEHICLES.items():
    (OUT / f'{name}.svg').write_text(svg(73, 33, inner, title)); count += 1
for name, (w, h, title, inner) in SECTION.items():
    (OUT / f'{name}.svg').write_text(svg(w, h, inner, title)); count += 1
print(f'wrote {count} icons to {OUT}')
