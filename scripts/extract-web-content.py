"""Extract the reviewed static pages into Next.js content: shared shell fragments, page bodies and the route registry.

RETIRED after the Next.js migration: content/ is now the source of truth and has newer edits than the
static reference pages. Re-running this would overwrite them. Edit content/ directly instead.

Run once per content refresh from the repository root:  python3 scripts/extract-web-content.py
The static pages remain the design reference; apps/web renders the extracted fragments.
"""
import html, json, pathlib, re

import sys
if '--force' not in sys.argv:
    sys.exit('Retired: edit content/ directly (pass --force only to rebuild content from the static reference).')
ROOT = pathlib.Path(__file__).resolve().parents[1]
CONTENT = ROOT / 'content'
(CONTENT / 'pages').mkdir(parents=True, exist_ok=True)
(CONTENT / 'shell').mkdir(parents=True, exist_ok=True)

PAGES = [  # id, static source, public path, family
    ('home', 'index.html', '/', 'homepage'),
    ('locations', 'locations/index.html', '/locations/', 'service-area-directory'),
    ('about', 'about/index.html', '/about/', 'company'),
    ('faq', 'faq/index.html', '/faq/', 'faq'),
    ('contact', 'contact/index.html', '/contact/', 'company'),
    ('privacy-policy', 'privacy-policy/index.html', '/privacy-policy/', 'legal'),
]


def section(s, start, end):
    i, j = s.index(start), s.index(end)
    return s[i:j]


home = (ROOT / 'index.html').read_text()
body_start = re.search(r'<body[^>]*>', home).end()
sprite = re.match(r'\s*(<svg aria-hidden="true" id="__SVG_SPRITE_NODE__".*?</svg>)', home[body_start:], re.S).group(1)
after_sprite = body_start + home[body_start:].index(sprite) + len(sprite)
header = home[after_sprite:home.index('<main class="main">')]
header = re.sub(r'<!--.*?-->', '', header, flags=re.S).strip()
footer = home[home.index('</main>') + len('</main>'):home.index('</footer>') + len('</footer>')].strip()
inline_css = '\n'.join(re.findall(r'<style>(.*?)</style>', home[:home.index('</head>')], re.S))

(CONTENT / 'shell' / 'sprite.svg').write_text(sprite + '\n')
(CONTENT / 'shell' / 'header.html').write_text(header + '\n')
(CONTENT / 'shell' / 'footer.html').write_text(footer + '\n')
(ROOT / 'apps/web/public/css').mkdir(parents=True, exist_ok=True)
(ROOT / 'apps/web/public/css/inline.css').write_text('/* Extracted from the reference page head */\n' + inline_css.strip() + '\n')

registry = {'version': 1, 'maxPublicContentPages': 10,
            'note': 'Owner approval required: set status "published", add "production" to environments and record approval before release.',
            'routes': []}
old = {}
reg_path = CONTENT / 'publication.json'
if reg_path.exists():
    old = {r['id']: r for r in json.loads(reg_path.read_text())['routes']}

for pid, src, path, family in PAGES:
    s = (ROOT / src).read_text()
    main = s[s.index('<main class="main">') + len('<main class="main">'):s.index('</main>')].strip()
    (CONTENT / 'pages' / f'{pid}.html').write_text(main + '\n')
    title = html.unescape(re.search(r'<title>(.*?)</title>', s, re.S).group(1))
    desc = html.unescape(re.search(r'<meta content="([^"]*)" name="description"/>', s).group(1))
    ld = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', s, re.S).group(1))
    prev = old.get(pid, {})
    registry['routes'].append({
        'id': pid, 'path': path, 'family': family, 'title': title, 'description': desc, 'jsonLd': ld,
        'status': prev.get('status', 'review'),
        'environments': prev.get('environments', ['local', 'development']),
        'approval': prev.get('approval'),
    })

reg_path.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + '\n')
print('extracted', len(PAGES), 'pages, header, footer and sprite into content/')
